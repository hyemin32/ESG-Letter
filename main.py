"""
ESG 뉴스레터 자동화 - 메인 실행기.

동작 순서:
  1) 오늘 날짜(KST) 계산, 아카이브 로드
  2) Google 뉴스 RSS에서 후보 수집 → 국내/해외 할당량만큼 선별 + 본문 추출
  3) 쓸 만한 기사가 부족하면 → ESG 용어 특별편
  4) 충분하면 → Gemini로 요약/번역/연속성/용어, 참고 링크 생성
  5) 웹 뉴스레터(HTML) + 아카이브 index 생성, 아카이브 갱신
  6) Slack으로 요약 + 링크 발송
매 단계는 부분 실패에 관대하고, 완전 실패 시 Slack으로 알립니다.
"""
from __future__ import annotations

import os
import sys
import traceback
from datetime import datetime, timezone, timedelta

import config
from src import archive, fetch_news, select, gemini_ai, links, render, slack

# 로컬 실행 시 .env 파일이 있으면 환경변수로 읽어들인다 (GitHub Actions에선 무시됨).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def today_kst() -> str:
    """KST(UTC+9) 기준 오늘 날짜 문자열 YYYY-MM-DD."""
    return (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%Y-%m-%d")


def page_url(day: str) -> str:
    """Slack에 넣을 뉴스레터 웹페이지 주소."""
    base = os.environ.get("SITE_BASE_URL", "").rstrip("/")
    return f"{base}/{day}.html" if base else f"{day}.html"


def run() -> int:
    day = today_kst()
    print(f"===== ESG 레터 실행 {day} =====")
    data = archive.load()

    # 1) 뉴스 후보 수집 & 선별
    candidates = fetch_news.collect_candidates()
    exclude = archive.recent_urls(data)
    articles = select.select_articles(candidates, exclude_urls=exclude)

    # 2) 조용한 날 → 용어 특별편
    if len(articles) < config.QUIET_DAY_THRESHOLD:
        print("[main] 기사 부족 → ESG 용어 특별편으로 전환")
        special = gemini_ai.special_edition(archive.covered_terms(data))
        if not special:
            slack.send_failure(day, "기사도 부족하고 특별편 생성도 실패")
            return 1
        render.render_special(day, special)
        archive.append_special(data, day, special.get("term", ""))
        render.render_index(data)
        archive.save(data)
        slack.send_special(day, page_url(day), special)
        return 0

    # 3) 기사별 요약/번역/연속성/용어 + 참고 링크
    recent_ctx = archive.continuity_context(data)
    finished: list = []
    for art in articles:
        if gemini_ai.summarize(art, recent_ctx):
            art.extra_links = links.build_extra_links(art)
            finished.append(art)
        else:
            print(f"[main] 요약 실패로 제외: {art.title[:50]}")

    if not finished:
        slack.send_failure(day, "모든 기사 요약에 실패")
        return 1

    # 4) 웹페이지 + 아카이브 생성
    intro = (f"오늘은 ESG 소식 {len(finished)}건을 준비했어요. "
             f"각 기사의 요약과 이해를 돕는 링크를 함께 담았습니다.")
    render.render_daily(day, intro, finished)
    archive.append_daily(data, day, finished)
    render.render_index(data)
    archive.save(data)

    # 5) Slack 발송
    slack.send_daily(day, page_url(day), finished)
    print(f"===== 완료: {len(finished)}건 발행 =====")
    return 0


def main() -> int:
    day = today_kst()
    try:
        return run()
    except Exception as exc:
        print("[main] 치명적 오류:\n" + traceback.format_exc())
        try:
            slack.send_failure(day, f"예외 발생: {exc}")
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
