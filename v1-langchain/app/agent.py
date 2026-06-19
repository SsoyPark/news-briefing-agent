from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from datetime import date
from tools import get_tools

def create_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    today = date.today().strftime("%Y년 %m월 %d일")
    tools = get_tools()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""당신은 오늘({today}) 최신 뉴스를 검색하고 브리핑하는 AI 에이전트입니다.

반드시 search_keyword_news와 search_top_news 툴을 사용해서 실제 뉴스를 검색하세요.
[오늘의 이슈]는 반드시 search_top_news 툴로만 가져오고, 
검색 키워드와 완전히 무관한 오늘의 핫한 뉴스여야 합니다.
         
오늘 날짜가 아닌 기사는 절대 사용하지 마세요.
         
중요: 링크는 반드시 검색 결과에서 가져온 실제 URL을 그대로 사용하세요.
링크를 절대 생략하거나 수정하지 마세요.

답변은 반드시 아래 형식만 사용하세요:

[핵심 요약]
- 요약 1
- 요약 2
- 요약 3

[주요 뉴스]
제목: 뉴스 제목1
링크: https://...
요약: 한줄 요약
제목: 뉴스 제목2
링크: https://...
요약: 한줄 요약
제목: 뉴스 제목3
링크: https://...
요약: 한줄 요약

[시사점]
- 시사점 1
- 시사점 2
- 시사점 3

[연관 뉴스]
제목: 뉴스 제목1
링크: https://...
연관이유: 한줄
제목: 뉴스 제목2
링크: https://...
연관이유: 한줄
제목: 뉴스 제목3
링크: https://...
연관이유: 한줄

[오늘의 이슈]
제목: 뉴스 제목1
링크: https://...
요약: 한줄 요약
제목: 뉴스 제목2
링크: https://...
요약: 한줄 요약
제목: 뉴스 제목3
링크: https://...
요약: 한줄 요약
         
         
[감성 분석]
긍정: X%
부정: X%
중립: X%

개별 분석:
1. (제목) - 긍정/부정/중립 - 이유 한줄
2. (제목) - 긍정/부정/중립 - 이유 한줄
3. (제목) - 긍정/부정/중립 - 이유 한줄
         
[주식 시세]
기업: 기업명
현재가: X,XXX원
등락: ▲/▼ XX원 (+X.XX%)
거래량: XXX,XXX주
당일고가: X,XXX원
당일저가: X,XXX원
52주최고: X,XXX원
52주최저: X,XXX원
         
         """),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

def extract_section(text, section):
    if f"[{section}]" not in text:
        return ""
    parts = text.split(f"[{section}]")
    if len(parts) < 2:
        return ""
    content = parts[1]
    for next_section in ["[핵심 요약]", "[주요 뉴스]", "[시사점]", "[연관 뉴스]", "[오늘의 이슈]"]:
        if next_section in content:
            content = content.split(next_section)[0]
    return content.strip()

def run_agent(keyword: str, agent_executor=None) -> dict:
    if agent_executor is None:
        agent_executor = create_agent()
    today = date.today().strftime("%Y년 %m월 %d일")
    
    company_list = ["삼성전자", "sk하이닉스", "현대차", "현대자동차", "카카오",
                    "네이버", "naver", "lg전자", "셀트리온", "기아", "포스코",
                    "kb금융", "신한지주", "하나금융", "sk텔레콤", "skt", "kt", "lg화학"]
    is_company = keyword.lower().strip() in company_list

    # 에이전트: 뉴스 검색만 (주식/이슈/감성 제외)
    result = agent_executor.invoke({
        "input": f"""
        오늘({today}) 다음 순서대로 실행해줘:
        1. search_keyword_news로 '{keyword}' 뉴스 검색
        2. search_related_news로 '{keyword}' 연관 뉴스 검색

        반드시 형식에 맞게 [핵심 요약], [주요 뉴스], [시사점], [연관 뉴스] 만 답변해줘.
        """
    })
    output = result["output"]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 주식 시세 — 직접 호출
    import yfinance as yf
    ticker_map = {
        "삼성전자": "005930.KS", "sk하이닉스": "000660.KS",
        "현대차": "005380.KS", "현대자동차": "005380.KS",
        "카카오": "035720.KS", "네이버": "035420.KS",
        "lg전자": "066570.KS", "셀트리온": "068270.KS",
        "기아": "000270.KS", "포스코": "005490.KS",
        "kb금융": "105560.KS", "신한지주": "055550.KS",
        "하나금융": "086790.KS", "sk텔레콤": "017670.KS",
        "skt": "017670.KS", "kt": "030200.KS", "lg화학": "051910.KS",
    }
    ticker = ticker_map.get(keyword.lower().strip())

    if is_company and ticker:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            hist_year = stock.history(period="1y")
            current = hist["Close"].iloc[-1]
            open_price = hist["Open"].iloc[-1]
            high = hist["High"].iloc[-1]
            low = hist["Low"].iloc[-1]
            change = current - open_price
            change_pct = (change / open_price) * 100
            volume = hist["Volume"].iloc[-1]
            week52_high = hist_year["High"].max()
            week52_low = hist_year["Low"].min()
            direction = "▲" if change > 0 else "▼" if change < 0 else "-"
            stock_output = (
                f"기업: {keyword}\n"
                f"현재가: {current:,.0f}원\n"
                f"등락: {direction} {abs(change):,.0f}원 ({change_pct:+.2f}%)\n"
                f"거래량: {volume:,}주\n"
                f"당일고가: {high:,.0f}원\n"
                f"당일저가: {low:,.0f}원\n"
                f"52주최고: {week52_high:,.0f}원\n"
                f"52주최저: {week52_low:,.0f}원"
            )
        except:
            stock_output = ""
    else:
        # 상위 5개 — 현재가 + 등락만
        top_stocks = {
            "삼성전자": "005930.KS", "SK하이닉스": "000660.KS",
            "현대차": "005380.KS", "기아": "000270.KS", "네이버": "035420.KS",
        }
        lines = []
        for name, t in top_stocks.items():
            try:
                s = yf.Ticker(t)
                h = s.history(period="1d")
                if h.empty:
                    continue
                cur = h["Close"].iloc[-1]
                op = h["Open"].iloc[-1]
                chg = cur - op
                chg_pct = (chg / op) * 100
                direction = "▲" if chg_pct > 0 else "▼" if chg_pct < 0 else "-"
                lines.append(
                    f"기업: {name}\n"
                    f"현재가: {cur:,.0f}원\n"
                    f"등락: {direction} {abs(chg):,.0f}원 ({chg_pct:+.2f}%)"
                )
            except:
                continue
        stock_output = "\n\n".join(lines)

    # 오늘의 이슈 — 직접 호출
    from tools import naver_news_search
    issue_raw = naver_news_search("오늘 한국 사회 경제 정치 이슈")
    issue_result = llm.invoke(f"""
아래 뉴스 검색 결과를 보고 오늘의 주요 이슈 3개를 골라줘.
검색 키워드({keyword})와 무관한 뉴스만 선택해줘.

{issue_raw}

반드시 아래 형식으로만 답변해:
제목: 뉴스 제목1
링크: https://...
요약: 한줄 요약
제목: 뉴스 제목2
링크: https://...
요약: 한줄 요약
제목: 뉴스 제목3
링크: https://...
요약: 한줄 요약
""")
    issue_output = issue_result.content

    # 감성 분석
    main_news = extract_section(output, "주요 뉴스")
    sentiment_result = llm.invoke(f"""
아래 뉴스 3개의 감성을 분석해줘.

{main_news}

반드시 아래 형식으로만 답변해. 줄바꿈을 정확히 지켜줘:

긍정: X%
부정: X%
중립: X%

1. [긍정] 뉴스 제목 - 이유 한줄
2. [부정] 뉴스 제목 - 이유 한줄
3. [중립] 뉴스 제목 - 이유 한줄
""")
    sentiment_output = sentiment_result.content

    return {
        "summary": extract_section(output, "핵심 요약"),
        "main": extract_section(output, "주요 뉴스"),
        "insight": extract_section(output, "시사점"),
        "related": extract_section(output, "연관 뉴스"),
        "issue": issue_output,
        "sentiment": sentiment_output,
        "stock": stock_output
    }