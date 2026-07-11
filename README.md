# 🌱 오늘의 ESG 레터

매 평일 아침, ESG 뉴스를 자동으로 모아 요약하고 **Slack으로 알림**을 보내며,
**웹 뉴스레터(GitHub Pages)** 에 아카이브로 쌓아두는 무인 자동화 시스템입니다.

## 무엇을 하나요
- 📰 **Google 뉴스 RSS**에서 국내·해외 ESG 기사 수집
- ✂️ 하루 **5건**(국내 2 + 해외 3) 선별, 원문 본문 추출
- 🤖 **Gemini**로 한국어 요약·번역, 핵심 용어 추출, 이전 이슈와의 **연속성** 표시
- 🔗 위키백과·관련뉴스 등 **이해를 돕는 참고 링크**(지어낸 URL 없음)
- 📅 조용한 날엔 **ESG 용어 특별편**(중복 없이 새 용어)
- 📲 **Slack**으로 요약 + 웹페이지 링크 발송, **GitHub Pages**에 영구 보관

## 처음이라면
👉 **[SETUP.md](SETUP.md)** 를 순서대로 따라 하세요 (약 30분, 코딩 지식 불필요).

## 구조
```
main.py                  전체 실행 흐름
config.py                설정(기사 수·키워드·비율 등)
src/
  fetch_news.py          Google 뉴스 RSS 수집
  scrape.py              구글 링크 → 원문 URL 디코딩 + 본문 추출
  select.py              국내/해외 할당량 선별·중복 제거
  gemini_ai.py           요약·번역·연속성·용어·특별편 (Gemini)
  links.py               참고 링크 생성
  archive.py             과거 기록(연속성·용어 중복 방지)
  render.py              웹 뉴스레터 HTML 생성
  slack.py               Slack 발송
.github/workflows/daily.yml   매 평일 07:00 KST 자동 실행
docs/                    GitHub Pages 발행 폴더(자동 생성)
archive/history.json     누적 기록
```

## 로컬에서 테스트
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # .env 를 열어 키 3개 채우기
python main.py
```
