"""
News Briefing MCP Server
========================
기존 LangChain 기반 뉴스 브리핑 에이전트(news-briefing-agent)의 도구를
MCP(Model Context Protocol) 표준 서버로 재구성한 버전.

설계 철학 (기존 에이전트에서 계승):
- 키워드 '의존' 작업(뉴스 검색)과 키워드 '독립' 작업(주식 시세 등)을 분리.
  호스트(LLM)는 판단이 필요한 검색 도구를 호출하고,
  결정적(deterministic)인 주식 조회는 인자로 받은 그대로 실행한다.
  → 에이전트 컨텍스트가 불필요한 데이터로 오염되는 것을 막는다.

도구 목록:
  1. search_keyword_news   - 키워드 최신 뉴스 검색 (네이버)
  2. search_related_news   - 키워드 연관 뉴스 검색 (네이버)
  3. search_top_news       - 오늘의 핫이슈 (키워드 무관)
  4. analyze_sentiment     - 뉴스 텍스트 감성 분석 (GPT)
  5. get_stock_price       - 한국 주식 시세 조회 (yfinance)
"""

from __future__ import annotations

import os
from dotenv import load_dotenv
load_dotenv()

from datetime import date
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("news-briefing")

# ---------------------------------------------------------------------------
# 공통: 네이버 뉴스 검색 (내부 헬퍼)
# ---------------------------------------------------------------------------
NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"


def _clean(text: str) -> str:
    """네이버 응답의 HTML 태그/엔티티 제거."""
    return (
        text.replace("<b>", "")
        .replace("</b>", "")
        .replace("&quot;", '"')
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )


def _naver_news_search(query: str, display: int = 5) -> list[dict[str, str]]:
    """네이버 뉴스 API 호출 → 구조화된 기사 리스트 반환.

    문자열 대신 dict 리스트로 반환해 MCP 클라이언트가 파싱하기 쉽게 했다.
    """
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수가 설정되지 않았습니다."
        )

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {"query": query, "display": display, "sort": "date"}

    resp = requests.get(NAVER_NEWS_URL, headers=headers, params=params, timeout=10)
    resp.raise_for_status()

    items = resp.json().get("items", [])
    articles: list[dict[str, str]] = []
    for item in items:
        url = (item.get("originallink") or "").strip() or (item.get("link") or "").strip()
        articles.append(
            {
                "title": _clean(item.get("title", "")),
                "summary": _clean(item.get("description", "")),
                "url": url,
                "pubDate": item.get("pubDate", ""),
            }
        )
    return articles


# ---------------------------------------------------------------------------
# 1~3. 뉴스 검색 도구 (키워드 의존 / 독립)
# ---------------------------------------------------------------------------
@mcp.tool()
def search_keyword_news(keyword: str) -> list[dict[str, str]]:
    """주어진 키워드의 오늘자 최신 뉴스를 검색한다.

    Args:
        keyword: 검색할 키워드 (예: '삼성전자', 'AI 반도체')
    Returns:
        제목/요약/링크/발행일을 담은 기사 리스트
    """
    return _naver_news_search(keyword)


@mcp.tool()
def search_related_news(keyword: str) -> list[dict[str, str]]:
    """키워드와 연관된 동향 뉴스를 검색한다.

    Args:
        keyword: 기준 키워드. 내부적으로 '<keyword> 동향'으로 질의한다.
    """
    return _naver_news_search(f"{keyword} 동향")


@mcp.tool()
def search_top_news() -> list[dict[str, str]]:
    """검색 키워드와 무관한 오늘의 한국 주요 이슈 뉴스를 가져온다.

    키워드 '독립' 도구. 고정 질의를 사용하므로 인자가 없다.
    """
    return _naver_news_search("오늘 한국 사회 경제 정치 이슈 핫뉴스")


# ---------------------------------------------------------------------------
# 4. 감성 분석 (GPT)
# ---------------------------------------------------------------------------
@mcp.tool()
def analyze_sentiment(news_text: str) -> str:
    """뉴스 텍스트의 감성을 긍정/부정/중립 비율로 분석한다.

    Args:
        news_text: 분석할 뉴스 제목/요약 묶음 텍스트
    Returns:
        전체 비율 + 개별 분석이 담긴 텍스트
    """
    # 지연 임포트: 감성 분석을 안 쓰는 호출에서는 openai 의존성을 끌어오지 않음
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = f"""아래 뉴스 텍스트들의 감성을 분석해줘.
각 뉴스마다 긍정/부정/중립 중 하나로 분류하고, 전체 비율을 퍼센트로 계산해줘.

뉴스 텍스트:
{news_text}

반드시 아래 형식으로만 답변해:
긍정: X%
부정: X%
중립: X%

개별 분석:
1. (제목) - 긍정/부정/중립 - 이유 한줄
2. (제목) - 긍정/부정/중립 - 이유 한줄
3. (제목) - 긍정/부정/중립 - 이유 한줄
"""
    return llm.invoke(prompt).content


# ---------------------------------------------------------------------------
# 5. 주식 시세 (yfinance) — agent.py에 흩어져 있던 로직을 독립 도구로 승격
# ---------------------------------------------------------------------------
TICKER_MAP: dict[str, str] = {
    "삼성전자": "005930.KS", "sk하이닉스": "000660.KS",
    "현대차": "005380.KS", "현대자동차": "005380.KS",
    "카카오": "035720.KS", "네이버": "035420.KS", "naver": "035420.KS",
    "lg전자": "066570.KS", "셀트리온": "068270.KS", "기아": "000270.KS",
    "포스코": "005490.KS", "kb금융": "105560.KS", "신한지주": "055550.KS",
    "하나금융": "086790.KS", "sk텔레콤": "017670.KS", "skt": "017670.KS",
    "kt": "030200.KS", "lg화학": "051910.KS",
}


@mcp.tool()
def get_stock_price(company: str, include_52week: bool = False) -> dict[str, Any]:
    """한국 기업명을 받아 당일 주식 시세를 조회한다 (yfinance).

    키워드 '독립' 도구: LLM 판단 없이 인자로 받은 기업명을 그대로 조회한다.

    Args:
        company: 기업명 (예: '삼성전자', 'SK하이닉스')
        include_52week: True면 52주 최고/최저도 조회한다 (느려짐). 기본 False.
    Returns:
        현재가/등락/거래량 등을 담은 dict.
        매핑되지 않은 기업명이면 error 키를 담아 반환한다.
    """
    import yfinance as yf

    ticker = TICKER_MAP.get(company.lower().strip())
    if not ticker:
        return {"error": f"'{company}'는 지원하지 않는 기업명입니다.",
                "supported": sorted(set(TICKER_MAP.keys()))}

    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    if hist.empty:
        return {"error": f"'{company}' 시세 데이터를 가져오지 못했습니다."}

    current = float(hist["Close"].iloc[-1])
    open_price = float(hist["Open"].iloc[-1])
    change = current - open_price
    change_pct = (change / open_price) * 100 if open_price else 0.0
    direction = "▲" if change > 0 else "▼" if change < 0 else "-"

    result: dict[str, Any] = {
        "company": company,
        "ticker": ticker,
        "current_price": round(current),
        "change": round(change),
        "change_pct": round(change_pct, 2),
        "direction": direction,
        "volume": int(hist["Volume"].iloc[-1]),
        "day_high": round(float(hist["High"].iloc[-1])),
        "day_low": round(float(hist["Low"].iloc[-1])),
        "as_of": date.today().isoformat(),
    }

    # 52주 고저는 선택적으로만 조회 (1년치 데이터라 느림)
    if include_52week:
        hist_year = stock.history(period="1y")
        if not hist_year.empty:
            result["week52_high"] = round(float(hist_year["High"].max()))
            result["week52_low"] = round(float(hist_year["Low"].min()))

    return result


# ---------------------------------------------------------------------------
# 엔트리포인트
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # stdio 트랜스포트: Claude Desktop / MCP Inspector 양쪽과 호환
    mcp.run(transport="stdio")
