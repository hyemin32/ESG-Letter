"""
ESG 뉴스레터 자동화 - 설정 파일.

이 파일의 값만 바꾸면 뉴스레터 동작을 조정할 수 있습니다.
(코드를 몰라도 아래 숫자와 단어만 고치면 됩니다.)
"""

# ── 하루에 다룰 기사 개수 ─────────────────────────────
TOTAL_ARTICLES = 5          # 하루 총 기사 수
DOMESTIC_COUNT = 2          # 그 중 국내 기사 (해외 = TOTAL - DOMESTIC)
GLOBAL_COUNT = TOTAL_ARTICLES - DOMESTIC_COUNT

# 쓸 만한 기사가 이 개수 미만이면 "ESG 용어 특별편"으로 전환
QUIET_DAY_THRESHOLD = 2

# ── 뉴스 검색 키워드 (Google 뉴스 RSS) ─────────────────
# 국내: 한국어 키워드 (한국 지역·언어로 검색)
DOMESTIC_QUERIES = [
    "ESG",
    "탄소중립",
    "지속가능경영",
    "ESG 공시",
    "탄소배출",
]
# 해외: 영어 키워드 (전 세계 영어 뉴스, 한국어로 번역·요약함)
GLOBAL_QUERIES = [
    "ESG regulation",
    "carbon emissions",
    "sustainability disclosure",
    "climate policy",
    "net zero",
]

# 최근 며칠 이내 기사만 후보로 (오래된 기사 배제)
ARTICLE_MAX_AGE_HOURS = 36

# ── 연속성(이전 이슈 연결) ─────────────────────────────
CONTINUITY_LOOKBACK_DAYS = 30   # 며칠 전까지 아카이브를 참조할지

# ── 발행처 정보 ──────────────────────────────────────
NEWSLETTER_TITLE = "오늘의 ESG 레터"
TIMEZONE = "Asia/Seoul"

# ── Gemini 모델 ──────────────────────────────────────
# 무료 티어에서 쓸 수 있는 모델. 모델마다 무료 quota가 따로라 429가 뜨면 바꿔볼 것.
# 후보: "gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"
GEMINI_MODEL = "gemini-2.5-flash"

# ── 경로 (건드리지 않아도 됨) ───────────────────────────
ARCHIVE_PATH = "archive/history.json"
DOCS_DIR = "docs"               # GitHub Pages가 발행하는 폴더
