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

- **ReAct 에이전트** — Reasoning + Acting 패턴으로 검색 → 분석 → 브리핑 자동 수행
- **Tavily 검색 툴** — AI 최적화 웹 검색으로 최신 뉴스 수집
- **구조화 브리핑** — 핵심 요약 / 주요 뉴스 3개 / 시사점 형식으로 출력
- **Streamlit UI** — 키워드 입력 후 바로 결과 확인
- **Docker** — 단일 명령어로 실행 환경 구성

---

## 아키텍처
키워드 입력
↓
ReAct 에이전트 (Langchain)
↓
Tavily 검색 툴 실행
↓
결과 분석 및 브리핑 생성 (GPT-4o-mini)
↓
Streamlit UI 출력

---

## 기술 스택

| 구분 | 기술 |
|---|---|
| 에이전트 | Langchain 0.2.16 / ReAct |
| LLM | OpenAI GPT-4o-mini |
| 검색 | Tavily API |
| UI | Streamlit |
| 배포 | Docker / Docker Compose |

---

## 실행 방법

### 사전 준비

- Docker Desktop 설치
- OpenAI API 키
- Tavily API 키

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

## 개발자

**박소영** · AI/ML Engineer

- GitHub: [@SsoyPark](https://github.com/SsoyPark)
- Velog: [@ssoypark](https://velog.io/@ssoypark)
