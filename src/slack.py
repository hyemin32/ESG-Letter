"""Slack Incoming Webhook으로 그날의 요약 + 뉴스레터 링크를 보낸다."""
from __future__ import annotations

import json
import os

import requests

from src.models import Article


def _post(text: str) -> bool:
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url:
        print("[slack] SLACK_WEBHOOK_URL 없음 — 발송 건너뜀\n" + text)
        return False
    try:
        r = requests.post(url, data=json.dumps({"text": text}),
                          headers={"Content-Type": "application/json"}, timeout=15)
        if r.status_code == 200:
            print("[slack] 발송 완료")
            return True
        print(f"[slack] 발송 실패 {r.status_code}: {r.text[:120]}")
        return False
    except Exception as exc:
        print(f"[slack] 발송 오류: {exc}")
        return False


def send_daily(day: str, page_url: str, articles: list[Article]) -> bool:
    lines = [f"🌱 *오늘의 ESG 레터* · {day}",
             f"오늘 다룬 ESG 뉴스 {len(articles)}건을 정리했어요.\n"]
    for i, a in enumerate(articles, 1):
        tag = "🇰🇷" if a.region == "domestic" else "🌍"
        head = a.headline_ko or a.title
        lines.append(f"{i}. {tag} *{head}*")
        if a.summary:
            lines.append(f"    {a.summary[0]}")
    lines.append(f"\n👉 <{page_url}|전체 뉴스레터 웹에서 읽기>")
    return _post("\n".join(lines))


def send_special(day: str, page_url: str, special: dict) -> bool:
    text = (
        f"🌱 *오늘의 ESG 레터* · {day} (용어 특별편)\n"
        f"오늘은 뉴스가 조용해 ESG 용어를 하나 정리했어요. 📚\n\n"
        f"📖 *{special.get('term','')}*\n"
        f"    {special.get('one_liner','')}\n\n"
        f"👉 <{page_url}|웹에서 자세히 읽기>"
    )
    return _post(text)


def send_failure(day: str, reason: str) -> bool:
    return _post(f"⚠️ *ESG 레터 생성 실패* · {day}\n사유: {reason}\n"
                 f"로그를 확인해 주세요.")
