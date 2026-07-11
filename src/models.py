"""공용 데이터 구조."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """기사 하나를 표현. 파이프라인을 거치며 필드가 채워집니다."""
    title: str
    url: str                      # 최종(원문) 링크
    source: str                   # 언론사 이름
    published: Optional[datetime] # 발행 시각
    region: str                   # "domestic" | "global"
    query: str                    # 어떤 검색어로 찾았는지

    body: str = ""                # 스크래핑한 본문
    # --- 아래는 Gemini가 채움 ---
    headline_ko: str = ""         # 한국어 제목(해외 기사는 번역)
    summary: list[str] = field(default_factory=list)  # 3~4줄 요약
    why_important: str = ""       # 왜 중요한지 1줄
    terms: list[str] = field(default_factory=list)    # 핵심 ESG 용어
    continuity: str = ""          # 이전 이슈 연결 문구 (없으면 "")
    extra_links: list[dict] = field(default_factory=list)  # {"label","url"}

    def key(self) -> str:
        """중복 판단·아카이브 식별용."""
        return self.url
