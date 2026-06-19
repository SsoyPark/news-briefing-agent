# AI 뉴스 브리핑 에이전트 📰

> 키워드를 입력하면 오늘자 뉴스를 검색·분석해 브리핑을 자동 생성하는 AI 에이전트.
> 
> **V1 (LangChain Agent)** 에서 **V2 (MCP Server)** 로 아키텍처를 발전시킨 내용을 정리했다.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.2.16-green)
![MCP](https://img.shields.io/badge/MCP-FastMCP-purple)
![Docker](https://img.shields.io/badge/Docker-blue)

---

## 프로젝트 개요

키워드를 입력하면 네이버 뉴스 API로 오늘자 기사를 수집하고, 핵심 요약·감성 분석·주식 시세·오늘의 이슈를 자동으로 생성하는 뉴스 브리핑 에이전트이다.

같은 기능을 두 가지 아키텍처로 구현하며, Tool 설계를 발전시킨 과정을 담았다.

| | V1 — LangChain | V2 — MCP |
|---|---|---|
| 구조 | tool이 에이전트 앱 코드에 내장 | tool을 독립 MCP 서버로 분리 |
| 실행 | Streamlit UI 독립 실행 | Claude Desktop 등 호스트가 호출 |
| 재사용 | 해당 앱에서만 사용 가능 | 어떤 MCP 호스트에서도 재사용 |
| 검증 | 로컬 실행 확인 | MCP Inspector |
| 폴더 | [`v1-langchain/`](./v1-langchain) | [`v2-mcp/`](./v2-mcp) |

---

## V1 → V2 개발 과정

**V1**은 LangChain Tool Calling 에이전트로 구현했다. 뉴스 검색·감성분석·주식 시세 도구가 모두 에이전트 앱 코드 안에 들어 있어, Streamlit 앱 안에서만 동작한다.

**한계**: 도구들이 특정 앱에 종속되어, 다른 환경에서는 재사용할 수 없다.

**V2**에서는 이 도구들을 **MCP(Model Context Protocol) 표준 서버**로 분리하여, 어떤 MCP 호스트에서도 동일한 도구를 호출해 쓸 수 있는 구조로 만들었다. 
기능은 그대로 유지하면서 내부 구조만 개선했다.

> 두 버전은 동시에 쓰는 것이 아니라 용도에 따라 선택 가능
> 
> 독립적인 서비스가 필요하면 V1, 다른 AI 호스트에 도구를 제공하려면 V2.


---

## 기술 스택

| 구분 | V1 (LangChain) | V2 (MCP) |
|---|---|---|
| 에이전트 / 프로토콜 | LangChain Tool Calling | MCP (FastMCP) |
| 전송 / 실행 | Streamlit | stdio |
| 검증 | 로컬 실행 확인 | MCP Inspector |
| 공통 | OpenAI GPT-4o-mini · 네이버 뉴스 API · yfinance · Plotly | |

---

## 개발자

**박소영** · AI/ML Engineer

- GitHub: [@SsoyPark](https://github.com/SsoyPark)
- Velog: [@ssoypark](https://velog.io/@ssoypark)
