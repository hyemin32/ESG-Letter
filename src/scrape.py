"""Google 뉴스 링크를 원문 URL로 디코딩하고 본문을 추출한다."""
from __future__ import annotations

import trafilatura
from googlenewsdecoder import gnewsdecoder

from src.models import Article

MIN_BODY_CHARS = 250   # 이보다 짧으면 요약할 내용이 부족 → 스킵


def resolve_url(google_link: str) -> str | None:
    """news.google.com 링크를 실제 언론사 원문 URL로 변환."""
    try:
        res = gnewsdecoder(google_link, interval=1)
        if res.get("status") and res.get("decoded_url"):
            return res["decoded_url"]
    except Exception as exc:
        print(f"[scrape] URL 디코딩 실패: {exc}")
    return None


def fetch_body(url: str) -> str:
    """원문 URL에서 기사 본문 텍스트만 추출."""
    try:
        html = trafilatura.fetch_url(url)
        if not html:
            return ""
        text = trafilatura.extract(
            html, include_comments=False, include_tables=False
        )
        return (text or "").strip()
    except Exception as exc:
        print(f"[scrape] 본문 추출 실패 ({url[:50]}): {exc}")
        return ""


def hydrate(article: Article) -> bool:
    """기사에 원문 URL과 본문을 채운다. 성공하면 True."""
    real_url = resolve_url(article.url)
    if not real_url:
        return False
    article.url = real_url          # 구글 링크를 원문 링크로 교체
    article.body = fetch_body(real_url)
    if len(article.body) < MIN_BODY_CHARS:
        return False
    return True
