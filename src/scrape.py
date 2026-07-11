"""Google 뉴스 링크를 원문 URL로 디코딩하고 본문을 추출한다."""
from __future__ import annotations

import requests
import trafilatura
from googlenewsdecoder import gnewsdecoder

from src.models import Article

MIN_BODY_CHARS = 250   # 이보다 짧으면 요약할 내용이 부족 → 스킵
FETCH_TIMEOUT = 8      # 본문 다운로드 최대 대기 시간(초) — 느린 사이트 무한 대기 방지

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    )
}


def resolve_url(google_link: str) -> str | None:
    """news.google.com 링크를 실제 언론사 원문 URL로 변환."""
    try:
        # interval=0: 기사당 불필요한 대기 제거 (시도 횟수는 select에서 제한)
        res = gnewsdecoder(google_link, interval=0)
        if res.get("status") and res.get("decoded_url"):
            return res["decoded_url"]
    except Exception as exc:
        print(f"[scrape] URL 디코딩 실패: {exc}")
    return None


def fetch_body(url: str) -> str:
    """원문 URL에서 기사 본문 텍스트만 추출 (타임아웃 적용)."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=FETCH_TIMEOUT)
        if resp.status_code != 200 or not resp.text:
            return ""
        text = trafilatura.extract(
            resp.text, include_comments=False, include_tables=False
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
