"""후보 기사에서 지역별 할당량만큼 골라 본문까지 채운다."""
from __future__ import annotations

import time
from difflib import SequenceMatcher

import config
from src.models import Article
from src.scrape import hydrate

# 본문 추출(디코딩+다운로드)을 시도할 최대 횟수 — 후보를 하염없이 훑지 않도록 상한
MAX_HYDRATE_ATTEMPTS = 35
# 선별 단계 전체 제한 시간(초) — 이 시간을 넘기면 지금까지 고른 것으로 마감
TIME_BUDGET_SEC = 240


def _too_similar(title: str, chosen: list[Article]) -> bool:
    """이미 고른 기사와 제목이 매우 비슷하면(같은 사건) True."""
    for c in chosen:
        if SequenceMatcher(None, title, c.title).ratio() > 0.72:
            return True
    return False


def select_articles(
    candidates: list[Article],
    exclude_urls: set[str] | None = None,
) -> list[Article]:
    """
    최신순 후보를 훑으며 국내/해외 할당량을 채운다.
    - 이미 다룬(exclude_urls) 원문은 건너뜀
    - 같은 사건 중복 기사 제거
    - 본문 추출 실패 기사는 건너뜀 (부분 실패에 관대)
    """
    exclude_urls = exclude_urls or set()
    quota = {"domestic": config.DOMESTIC_COUNT, "global": config.GLOBAL_COUNT}
    chosen: list[Article] = []
    deadline = time.monotonic() + TIME_BUDGET_SEC
    attempts = 0

    for art in candidates:
        if quota["domestic"] <= 0 and quota["global"] <= 0:
            break
        if attempts >= MAX_HYDRATE_ATTEMPTS or time.monotonic() > deadline:
            print("[select] 시도 횟수/시간 상한 도달 → 선별 중단")
            break
        if quota[art.region] <= 0:
            continue
        if _too_similar(art.title, chosen):
            continue

        attempts += 1
        if not hydrate(art):        # 원문 URL 디코딩 + 본문 추출
            continue
        if art.url in exclude_urls: # 디코딩 후에야 원문 URL을 알 수 있음
            continue

        chosen.append(art)
        quota[art.region] -= 1
        print(f"[select] 채택 ({art.region}): {art.title[:50]}")

    # 한쪽 지역이 부족하면 다른 지역으로 총 개수를 채운다 (중요도 우선 유연 조정)
    shortfall = config.TOTAL_ARTICLES - len(chosen)
    if shortfall > 0:
        chosen_urls = {a.url for a in chosen}
        for art in candidates:
            if shortfall <= 0:
                break
            if attempts >= MAX_HYDRATE_ATTEMPTS or time.monotonic() > deadline:
                print("[select] 보충 단계 상한 도달 → 중단")
                break
            if art.url in chosen_urls or art in chosen:
                continue
            if _too_similar(art.title, chosen):
                continue
            attempts += 1
            if not hydrate(art):
                continue
            if art.url in exclude_urls or art.url in chosen_urls:
                continue
            chosen.append(art)
            chosen_urls.add(art.url)
            shortfall -= 1
            print(f"[select] 보충 채택 ({art.region}): {art.title[:50]}")

    print(f"[select] 최종 {len(chosen)}건 선정")
    return chosen
