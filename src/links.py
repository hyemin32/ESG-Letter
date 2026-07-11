"""핵심 용어로 '실제 존재하는' 참고 링크를 만든다 (URL 환각 방지: 검색 링크만 생성)."""
from __future__ import annotations

import urllib.parse

from src.models import Article

_WIKI = "https://ko.wikipedia.org/w/index.php?search={q}"
_GOOGLE = "https://www.google.com/search?q={q}"
_GNEWS = "https://news.google.com/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"


def _q(term: str) -> str:
    return urllib.parse.quote(term)


def build_extra_links(article: Article) -> list[dict]:
    """
    기사에서 뽑은 ESG 용어(article.terms)로 참고 링크 생성.
    - 각 용어: 위키백과 검색 링크 (용어 뜻)
    - 대표 용어: 관련 뉴스 검색 링크 (배경 기사)
    반환: [{"label": str, "url": str, "kind": "term"|"news"}]
    """
    links: list[dict] = []
    terms = [t for t in article.terms if t.strip()][:3]  # 최대 3개 용어

    for term in terms:
        links.append({
            "label": f"📖 {term} — 위키백과",
            "url": _WIKI.format(q=_q(term)),
            "kind": "term",
        })

    if terms:
        primary = terms[0]
        links.append({
            "label": f"🔎 '{primary}' 관련 뉴스 더 보기",
            "url": _GNEWS.format(q=_q(primary)),
            "kind": "news",
        })

    return links
