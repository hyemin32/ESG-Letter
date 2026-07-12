"""Gemini로 요약·번역·연속성 판단·용어추출, 그리고 용어 특별편을 생성한다."""
from __future__ import annotations

import json
import os
import time

from google import genai
from google.genai import types

import config
from src.models import Article

_CLIENT = None


def _client():
    global _CLIENT
    if _CLIENT is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY 환경변수가 없습니다. "
                "GitHub Secrets 또는 로컬 환경변수에 키를 넣어주세요."
            )
        # http 요청당 45초 제한 (AI 응답이 안 오면 멈추지 않게)
        _CLIENT = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=45_000),  # 밀리초
        )
    return _CLIENT


def _generate_json(prompt: str, retries: int = 2) -> dict | None:
    """Gemini에 JSON 응답을 요청하고 파싱. 무료 티어 분당 한도 대비 짧은 재시도 포함."""
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json", temperature=0.4
    )
    for attempt in range(retries):
        try:
            resp = _client().models.generate_content(
                model=config.GEMINI_MODEL, contents=prompt, config=cfg
            )
            return json.loads(resp.text)
        except Exception as exc:
            msg = str(exc)
            # 분당 한도(RPM)면 잠깐 쉬고 한 번만 더 시도 (하루 한도/미할당이면 어차피 소용없어 길게 안 기다림)
            if ("429" in msg or "quota" in msg.lower() or "rate" in msg.lower()) and attempt < retries - 1:
                print(f"[gemini] 한도 도달(429), 8초 후 1회 재시도... ({msg[:120]})")
                time.sleep(8)
                continue
            print(f"[gemini] 생성 실패: {msg[:200]}")
            return None
    return None


# ── 기사 요약/번역/연속성/용어 ────────────────────────────────
def summarize(article: Article, recent_context: list[dict]) -> bool:
    """article의 headline_ko/summary/why_important/terms/continuity를 채운다."""
    body = article.body[:4500]
    ctx_lines = [
        f'- {c["date"]}: {c["title"]} (용어: {", ".join(c.get("terms", []))})'
        for c in recent_context[:40]
    ]
    ctx_block = "\n".join(ctx_lines) if ctx_lines else "(최근 다룬 이슈 없음)"

    lang_note = (
        "이 기사는 해외(영문) 기사입니다. 제목과 요약을 반드시 한국어로 번역해서 작성하세요."
        if article.region == "global"
        else "이 기사는 국내 기사입니다."
    )

    prompt = f"""당신은 ESG 전문 뉴스레터 에디터입니다. 아래 기사를 한국어 독자를 위해 정리하세요.
{lang_note}

[기사 제목] {article.title}
[언론사] {article.source}
[본문]
{body}

[최근 30일간 이 뉴스레터가 다룬 이슈 목록]
{ctx_block}

다음 JSON 형식으로만 답하세요:
{{
  "headline_ko": "한국어 제목 (간결하게)",
  "summary": ["핵심 요약 문장 1", "문장 2", "문장 3"],
  "why_important": "이 기사가 왜 중요한지 한 문장",
  "terms": ["기사 속 핵심 ESG 용어 1~3개 (예: CBAM, 스코프3 배출)"],
  "continuity": "위 최근 이슈 목록 중 이 기사와 직접 이어지는 게 있으면 '지난 M/D에 다룬 OOO의 후속으로, ...' 형식으로 한 문장. 이어지는 게 없으면 빈 문자열."
}}
- summary는 3~4문장. 사실만, 과장 없이.
- terms는 독자가 검색해 볼만한 실제 ESG 전문 용어."""

    data = _generate_json(prompt)
    if not data:
        return False
    article.headline_ko = data.get("headline_ko", article.title).strip()
    article.summary = [s.strip() for s in data.get("summary", []) if s.strip()]
    article.why_important = data.get("why_important", "").strip()
    article.terms = [t.strip() for t in data.get("terms", []) if t.strip()]
    article.continuity = data.get("continuity", "").strip()
    return bool(article.summary)


# ── 조용한 날: ESG 용어 특별편 ────────────────────────────────
def special_edition(already_covered: list[str]) -> dict | None:
    """이미 다룬 용어를 피해 새 ESG 용어 하나를 골라 설명."""
    avoid = ", ".join(already_covered) if already_covered else "(없음)"
    prompt = f"""당신은 ESG 전문 뉴스레터 에디터입니다.
오늘은 다룰 주요 뉴스가 적어 'ESG 용어 특별편'을 만듭니다.
초보자도 이해할 수 있게 중요한 ESG 용어 하나를 골라 설명하세요.

[이미 다룬 용어 — 반드시 피할 것] {avoid}

다음 JSON 형식으로만 답하세요:
{{
  "term": "용어 이름 (한글, 필요시 영문 병기)",
  "one_liner": "한 문장 정의",
  "definition": "2~3문장의 쉬운 설명",
  "why_matters": "왜 중요한지 2문장",
  "example": "실제 사례나 비유 1개",
  "related_terms": ["관련 용어 2~3개"]
}}"""
    data = _generate_json(prompt)
    if not data or not data.get("term"):
        return None
    return data
