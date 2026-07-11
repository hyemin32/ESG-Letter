"""과거에 다룬 기사·용어 기록 (연속성 판단과 용어 중복 방지에 사용)."""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta

import config
from src.models import Article

_EMPTY = {"editions": [], "covered_terms": []}


def load() -> dict:
    if not os.path.exists(config.ARCHIVE_PATH):
        return json.loads(json.dumps(_EMPTY))
    try:
        with open(config.ARCHIVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("editions", [])
        data.setdefault("covered_terms", [])
        return data
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[archive] 로드 실패, 빈 아카이브로 시작: {exc}")
        return json.loads(json.dumps(_EMPTY))


def save(data: dict) -> None:
    os.makedirs(os.path.dirname(config.ARCHIVE_PATH), exist_ok=True)
    with open(config.ARCHIVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _recent_editions(data: dict, days: int) -> list[dict]:
    cutoff = date.today() - timedelta(days=days)
    out = []
    for ed in data.get("editions", []):
        try:
            d = datetime.strptime(ed["date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            continue
        if d >= cutoff:
            out.append(ed)
    return out


def recent_urls(data: dict, days: int = None) -> set[str]:
    """최근 N일 안에 이미 다룬 원문 URL 집합 (같은 기사 재탕 방지)."""
    days = days if days is not None else config.CONTINUITY_LOOKBACK_DAYS
    urls: set[str] = set()
    for ed in _recent_editions(data, days):
        for art in ed.get("articles", []):
            if art.get("url"):
                urls.add(art["url"])
    return urls


def continuity_context(data: dict, days: int = None) -> list[dict]:
    """Gemini에 넘길 최근 다룬 이슈 목록: [{date, title, terms}]."""
    days = days if days is not None else config.CONTINUITY_LOOKBACK_DAYS
    ctx: list[dict] = []
    for ed in _recent_editions(data, days):
        for art in ed.get("articles", []):
            ctx.append({
                "date": ed["date"],
                "title": art.get("title", ""),
                "terms": art.get("terms", []),
            })
    return ctx


def covered_terms(data: dict) -> list[str]:
    """특별편에서 이미 다룬 ESG 용어 (중복 방지)."""
    return data.get("covered_terms", [])


def append_daily(data: dict, day: str, articles: list[Article]) -> None:
    data["editions"].append({
        "date": day,
        "type": "daily",
        "articles": [
            {"url": a.url, "title": a.headline_ko or a.title, "terms": a.terms}
            for a in articles
        ],
    })


def append_special(data: dict, day: str, term: str) -> None:
    data["editions"].append({"date": day, "type": "special", "term": term})
    if term and term not in data["covered_terms"]:
        data["covered_terms"].append(term)
