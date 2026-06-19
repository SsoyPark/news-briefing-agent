# News Briefing MCP Server

기존 LangChain 기반 **뉴스 브리핑 에이전트**([news-briefing-agent](https://github.com/SsoyPark/news-briefing-agent))의 도구를
**MCP(Model Context Protocol)** 표준 서버로 재구성했다.

LangChain `@tool`로 에이전트 코드에 결합돼 있던 도구들을, 호스트(LLM 애플리케이션)와
분리된 표준 프로토콜 서버로 떼어내 **어떤 MCP 호스트에서도 재사용 가능**하도록 만들었다.

## 설계

원본 에이전트의 핵심 설계 방식(특성별 실행 방식 분리)을 MCP 구조에서도 유지했다.

| 구분 | 도구 | 특성 |
|------|------|------|
| 키워드 **의존** | `search_keyword_news`, `search_related_news` | LLM이 맥락을 보고 호출 여부·인자를 판단 |
| 키워드 **독립** | `search_top_news`, `get_stock_price` | LLM 판단 불필요 |
| 후처리 | `analyze_sentiment` | 수집된 텍스트에 대한 분석 |

키워드와 무관한 작업(오늘의 이슈, 주식 시세)을 LLM 호출 경로에서 분리함으로써,
에이전트 컨텍스트가 불필요한 데이터로 오염되는 것을 방지했다.

## 도구 목록

1. **search_keyword_news(keyword)** — 키워드의 오늘자 최신 뉴스 (네이버 뉴스 API)
2. **search_related_news(keyword)** — 키워드 연관 동향 뉴스
3. **search_top_news()** — 오늘의 한국 주요 이슈 (키워드 무관)
4. **analyze_sentiment(news_text)** — 긍정/부정/중립 비율 분석 (GPT)
5. **get_stock_price(company)** — 한국 주식 당일 시세 (yfinance)

모든 검색 도구는 문자열이 아닌 **구조화된 dict 리스트**를 반환해, 클라이언트가
파싱 없이 바로 활용할 수 있다.

## 설치

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

환경변수 설정:

```bash
cp .env.example .env
# .env에 네이버/OpenAI 키 입력
```

## 실행 & 테스트

### MCP Inspector (권장)

```bash
# 서버 단독 실행
python server.py

# 별도 터미널에서 Inspector 실행
npx @modelcontextprotocol/inspector python server.py
```

Inspector UI에서 각 도구를 직접 호출해 입출력을 확인할 수 있다.

### Claude Desktop

`claude_desktop_config.json`에 다음을 추가:

```json
{
  "mcpServers": {
    "news-briefing": {
      "command": "python",
      "args": ["/절대경로/news-mcp/server.py"],
      "env": {
        "NAVER_CLIENT_ID": "...",
        "NAVER_CLIENT_SECRET": "...",
        "OPENAI_API_KEY": "..."
      }
    }
  }
}
```

재시작 후 "삼성전자 주가 알려줘", "AI 반도체 뉴스 브리핑해줘" 등으로 도구 호출을 확인할 수 있다.

## 기술 스택

- **MCP**: `mcp[cli]` (공식 Python SDK, FastMCP)
- **트랜스포트**: stdio (Claude Desktop · MCP Inspector 호환)
- **데이터**: 네이버 뉴스 API, yfinance
- **분석**: OpenAI GPT-4o-mini
