# AI 뉴스 브리핑 에이전트 📰

> Langchain ReAct 에이전트가 키워드 기반 최신 뉴스를 검색·분석해 브리핑 자동 생성

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Langchain](https://img.shields.io/badge/Langchain-0.2.16-green)
![Streamlit](https://img.shields.io/badge/Streamlit-latest-red)
![Docker](https://img.shields.io/badge/Docker-blue)

---

## 프로젝트 소개

키워드를 입력하면 ReAct 에이전트가 Tavily 검색 툴을 활용해 최신 뉴스를 수집하고,
핵심 요약 · 주요 뉴스 · 시사점으로 구성된 브리핑 리포트를 자동 생성한다.

---

## 주요 기능

- **Langchain Tool Calling 에이전트** — LLM이 상황에 맞게 툴을 선택·실행
- **오늘자 뉴스 브리핑** — 네이버 뉴스 API 기반 최신 뉴스 수집 및 요약
- **감성 분석** — 주요 뉴스 3개의 긍정/부정/중립 비율 도넛 차트 시각화
- **주식 시세** — 기업명 검색 시 상세 시세, 일반 키워드 검색 시 코스피 상위 5개
- **오늘의 이슈** — 검색 키워드와 무관한 오늘의 핫한 뉴스 3개
- **세션 유지** — 새로고침해도 검색 결과 유지
- **Docker** — 단일 명령어로 실행 환경 구성

---

## 아키텍처
키워드 입력
↓
Tool Calling 에이전트 (Langchain)
├── search_keyword_news (네이버 뉴스 API)
└── search_related_news (네이버 뉴스 API)
↓
병렬 직접 호출
├── 감성 분석 (GPT-4o-mini)
├── 주식 시세 (yfinance)
└── 오늘의 이슈 (네이버 뉴스 API + GPT-4o-mini)
↓
Streamlit UI 출력

---

## 기술 스택

| 구분 | 기술 |
|---|---|
| 에이전트 | Langchain 0.2.16 / Tool Calling Agent |
| LLM | OpenAI GPT-4o-mini |
| 뉴스 검색 | 네이버 뉴스 API |
| 주식 시세 | yfinance |
| 감성 분석 | GPT-4o-mini + Plotly |
| UI | Streamlit |
| 배포 | Docker / Docker Compose |

---

## 실행 방법

### 사전 준비

- Docker Desktop 설치
- OpenAI API 키
- 네이버 개발자 센터 Client ID / Secret (https://developers.naver.com)

### 실행

```bash
# 레포 클론
git clone https://github.com/SsoyPark/news-briefing-agent.git
cd news-briefing-agent

# 환경변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 도커 실행
docker compose up --build
```

브라우저에서 `http://localhost:8501` 접속

---

## 스크린샷

<img width="1918" height="864" alt="image" src="https://github.com/user-attachments/assets/28756de7-69a8-4741-b301-758ef313eee7" />
<img width="1915" height="770" alt="image" src="https://github.com/user-attachments/assets/cfeb3084-7321-43fa-992d-89717c363a16" />
<img width="1906" height="793" alt="image" src="https://github.com/user-attachments/assets/21329904-dcb9-45c4-8e56-cb6872620139" />


---

## 개발자

**박소영** · AI/ML Engineer

- GitHub: [@SsoyPark](https://github.com/SsoyPark)
- Velog: [@ssoypark](https://velog.io/@ssoypark)
