# 🌱 ESG 레터 설치 가이드 (처음부터 끝까지)

코딩을 몰라도 순서대로 따라 하면 됩니다. 총 7단계, 약 30분이면 끝나요.
막히면 그 단계 번호를 알려주세요.

준비물: **GitHub 계정(있음)** + 아래에서 만들 **Gemini 키**, **Slack 웹훅** (둘 다 무료)

---

## 1단계 — GitHub에 코드 올리기

이 폴더(`ESG Letter`)를 GitHub 저장소로 올립니다. 가장 쉬운 방법은 **GitHub Desktop**입니다.

1. https://desktop.github.com 에서 GitHub Desktop 설치 → 내 계정으로 로그인
2. 상단 메뉴 **File → Add local repository** → 이 폴더(`C:\Users\hyemi\Desktop\AI\ESG Letter`) 선택
3. "이 폴더는 git 저장소가 아니다"라고 나오면 **create a repository** 클릭 → **Create repository**
4. 오른쪽 **Publish repository** 버튼 클릭
   - Name: `esg-letter` (이 이름 그대로 추천)
   - **"Keep this code private" 체크를 해제**하세요 (공개로 두어야 GitHub Pages가 무료로 됩니다)
   - **Publish** 클릭

> 이제 `https://github.com/<내아이디>/esg-letter` 에 코드가 올라갑니다.
> `<내아이디>` 부분을 메모해두세요 — 뒤에서 씁니다.

---

## 2단계 — Gemini API 키 발급 (무료)

기사를 요약해줄 AI 키입니다.

1. https://aistudio.google.com/apikey 접속 → 구글 계정으로 로그인
2. **Create API key**(API 키 만들기) 클릭
3. 만들어진 키(영문+숫자 긴 문자열)를 **복사**해서 메모장에 잠깐 붙여두세요

> 무료 티어로 충분합니다. 결제카드 등록 필요 없어요.

---

## 3단계 — Slack 워크스페이스 & 알림 받을 웹훅 만들기 (무료)

카톡처럼 폰으로 알림을 받을 곳입니다.

**3-1. 워크스페이스 준비**
- 이미 쓰는 Slack이 있으면 그걸 써도 됩니다.
- 없으면 https://slack.com/get-started 에서 새 워크스페이스를 무료로 만드세요.
- 폰에도 **Slack 앱**(플레이스토어)을 설치하고 같은 계정으로 로그인해두세요. (여기로 푸시가 옵니다)

**3-2. 알림 받을 채널 만들기**
- Slack에서 `#esg-레터` 같은 채널을 하나 만드세요 (기존 채널 써도 됨).

**3-3. Incoming Webhook 만들기**
1. https://api.slack.com/apps 접속 → **Create New App** → **From scratch**
2. App Name: `ESG Letter`, 워크스페이스 선택 → **Create App**
3. 왼쪽 메뉴 **Incoming Webhooks** → 오른쪽 스위치를 **On**
4. 아래 **Add New Webhook to Workspace** 클릭 → 알림 받을 **채널 선택** → **허용**
5. 생성된 **Webhook URL**(`https://hooks.slack.com/services/...`)을 **복사**해서 메모장에 붙여두세요

---

## 4단계 — GitHub에 비밀 키 3개 등록

방금 만든 키들을 GitHub에 안전하게 저장합니다. (코드에 직접 쓰지 않아요)

1. `https://github.com/<내아이디>/esg-letter` 접속 → 상단 **Settings**
2. 왼쪽 **Secrets and variables → Actions** 클릭
3. **Secrets** 탭에서 **New repository secret**으로 2개 등록:
   | Name (정확히 입력) | Secret 값 |
   |---|---|
   | `GEMINI_API_KEY` | 2단계에서 복사한 Gemini 키 |
   | `SLACK_WEBHOOK_URL` | 3단계에서 복사한 Slack 웹훅 URL |
4. **Variables** 탭으로 이동 → **New repository variable** 1개 등록:
   | Name | 값 |
   |---|---|
   | `SITE_BASE_URL` | `https://<내아이디>.github.io/esg-letter` |
   ( `<내아이디>` 를 본인 GitHub 아이디로 바꾸세요 )

---

## 5단계 — GitHub Pages 켜기 (뉴스레터 웹페이지)

1. 같은 **Settings** → 왼쪽 **Pages**
2. **Source**: `Deploy from a branch`
3. **Branch**: `main` 선택, 폴더는 `/docs` 선택 → **Save**

> 잠시 후 `https://<내아이디>.github.io/esg-letter/` 주소가 살아납니다.

---

## 6단계 — 자동화가 코드를 커밋할 수 있게 권한 열기

1. **Settings** → 왼쪽 **Actions → General**
2. 맨 아래 **Workflow permissions** → **Read and write permissions** 선택 → **Save**

> 이걸 해야 매일 만든 뉴스레터를 저장소에 저장할 수 있어요.

---

## 7단계 — 첫 발송 테스트 🚀

정해진 아침 시간까지 기다리지 않고 지금 바로 눌러서 확인합니다.

1. `https://github.com/<내아이디>/esg-letter` → 상단 **Actions** 탭
2. 왼쪽 **Daily ESG Letter** 클릭 → 오른쪽 **Run workflow** → 초록 **Run workflow** 버튼
3. 1~3분 뒤 초록 체크 ✅ 가 뜨면 성공
4. **Slack 앱**에 요약 메시지가 오는지 확인
5. 메시지의 링크(또는 `https://<내아이디>.github.io/esg-letter/오늘날짜.html`)를 열어 뉴스레터 확인

이후에는 **매주 월~금 오전 7시(한국시간)** 에 자동으로 도착합니다. 끝! 🎉

---

## ❓ 문제가 생기면

- **Actions가 빨간 X로 실패** → Actions에서 실패한 실행을 클릭하면 로그가 보입니다. 로그 마지막 부분을 저에게 보여주세요.
- **Slack 메시지가 안 옴** → 4단계의 `SLACK_WEBHOOK_URL` 값이 정확한지, 3단계에서 채널을 골랐는지 확인.
- **웹페이지가 404** → 5단계 Pages 설정에서 폴더를 `/docs`로 했는지, 첫 실행(7단계)을 한 번 돌렸는지 확인. (첫 실행 전에는 페이지가 비어 있어요)
- **요약이 이상하거나 실패** → `config.py`의 `GEMINI_MODEL`을 `"gemini-2.5-flash"`로 바꾸면 품질이 올라갑니다(무료 한도는 조금 더 빡빡).

## ⚙️ 나중에 바꾸고 싶을 때

- 다루는 **기사 수·국내해외 비율·키워드·발송 개수**는 전부 `config.py`에서 숫자만 고치면 됩니다.
- **발송 시간**은 `.github/workflows/daily.yml`의 `cron` 값에서 조정합니다 (현재 `0 22 * * 0-4` = 평일 7시 KST).
