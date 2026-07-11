"""Google 뉴스 RSS에서 ESG 기사 후보를 수집한다."""
from __future__ import annotations

import urllib.parse
from datetime import datetime, timezone, timedelta

import feedparser
from dateutil import parser as dateparser

import config
from src.models import Article

# 국내(한국어) / 해외(영어) RSS 엔드포인트 템플릿
_RSS_KO = "https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"
_RSS_EN = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def _parse_published(entry) -> datetime | None:
    raw = getattr(entry, "published", None) or getattr(entry, "updated", None)
    if not raw:
        return None
    try:
        dt = dateparser.parse(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def _source_name(entry) -> str:
    src = getattr(entry, "source", None)
    if src and getattr(src, "title", None):
        return src.title
    # Google 뉴스 제목은 보통 "기사 제목 - 언론사" 형태
    title = getattr(entry, "title", "")
    if " - " in title:
        return title.rsplit(" - ", 1)[-1].strip()
    return "출처 미상"


def _clean_title(entry) -> str:
    title = getattr(entry, "title", "").strip()
    if " - " in title:
        return title.rsplit(" - ", 1)[0].strip()
    return title


def _fetch_query(query: str, region: str) -> list[Article]:
    template = _RSS_KO if region == "domestic" else _RSS_EN
    url = template.format(q=urllib.parse.quote(query))
    feed = feedparser.parse(url)
    articles: list[Article] = []
    for entry in feed.entries:
        link = getattr(entry, "link", None)
        if not link:
            continue
        articles.append(
            Article(
                title=_clean_title(entry),
                url=link,
                source=_source_name(entry),
                published=_parse_published(entry),
                region=region,
                query=query,
            )
        )
    return articles


def collect_candidates() -> list[Article]:
    """모든 키워드에서 후보 기사를 모아 최신순으로 반환 (URL 중복 제거)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=config.ARTICLE_MAX_AGE_HOURS)
    seen: set[str] = set()
    out: list[Article] = []

    plan = [(q, "domestic") for q in config.DOMESTIC_QUERIES]
    plan += [(q, "global") for q in config.GLOBAL_QUERIES]

    for query, region in plan:
        try:
            for art in _fetch_query(query, region):
                if art.url in seen:
                    continue
                # 발행시각을 아는 기사는 신선도 필터 적용, 모르면 통과
                if art.published and art.published < cutoff:
                    continue
                seen.add(art.url)
                out.append(art)
        except Exception as exc:  # 한 쿼리 실패가 전체를 막지 않도록
            print(f"[fetch] '{query}' 수집 실패: {exc}")

    # 최신 우선 (발행시각 모르는 기사는 뒤로)
    out.sort(key=lambda a: a.published or datetime.min.replace(tzinfo=timezone.utc),
             reverse=True)
    print(f"[fetch] 후보 {len(out)}건 수집 (국내+해외)")
    return out
