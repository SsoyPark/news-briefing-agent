from langchain_community.tools.tavily_search import TavilySearchResults

# 뉴스 검색 툴

def get_tools():
    search = TavilySearchResults(
        max_results=5,              # 검색 결과 최대 개수
        search_depth="advanced",    # 더 깊이 있는 검색 수행
        include_answer=True,        # AI 요약 답변 포함
    )
    return [search]