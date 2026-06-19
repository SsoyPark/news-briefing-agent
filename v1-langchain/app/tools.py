from langchain.tools import tool
from datetime import date
import os
import requests
from langchain_openai import ChatOpenAI

def naver_news_search(query: str, display: int = 5) -> str:
    """네이버 뉴스 API로 검색"""
    headers = {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET")
    }
    params = {
        "query": query,
        "display": display,
        "sort": "date"  # 최신순 정렬
    }
    response = requests.get(
        "https://openapi.naver.com/v1/search/news.json",
        headers=headers,
        params=params
    )
    
    if response.status_code != 200:
        return f"뉴스 검색 실패: {response.status_code}"
    
    items = response.json().get("items", [])
    today = date.today().strftime("%Y%m%d")
    
    if not items:
        return f"'{query}' 관련 뉴스가 없습니다."
    
    articles = []
    for item in items:
        title = item["title"].replace("<b>", "").replace("</b>", "").replace("&quot;", '"')
        desc = item["description"].replace("<b>", "").replace("</b>", "").replace("&quot;", '"')
        # originallink 우선, 없으면 link 사용
        url = item.get("originallink", "").strip() or item.get("link", "").strip()
        articles.append(f"제목: {title}\n링크: {url}\n요약: {desc}")
    
    return "\n\n".join(articles)

@tool
def search_keyword_news(keyword: str) -> str:
    """키워드 관련 최신 뉴스를 검색합니다."""
    return naver_news_search(keyword)

@tool
def search_related_news(keyword: str) -> str:
    """키워드와 연관된 뉴스를 검색합니다."""
    return naver_news_search(f"{keyword} 동향")

@tool
def search_top_news(query: str = "오늘 주요 뉴스") -> str:
    """오늘 한국 주요 이슈 뉴스를 검색합니다. 검색 키워드와 완전히 무관한 오늘의 핫한 뉴스를 가져옵니다."""
    # 고정 쿼리 사용 — 키워드 무관하게 오늘 핫한 뉴스만
    return naver_news_search("오늘 한국 사회 경제 정치 이슈 핫뉴스")

@tool
def analyze_sentiment(news_text: str) -> str:
    """뉴스 텍스트의 감성을 분석합니다 (긍정/부정/중립 비율)."""
    
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    prompt = f"""
아래 뉴스 텍스트들의 감성을 분석해줘.
각 뉴스마다 긍정/부정/중립 중 하나로 분류하고,
전체 비율을 퍼센트로 계산해줘.

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
    response = llm.invoke(prompt)
    return response.content


def get_tools():
    return [search_keyword_news, search_related_news, search_top_news, analyze_sentiment]