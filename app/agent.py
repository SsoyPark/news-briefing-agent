from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents.react.agent import create_react_agent
from langchain import hub
from tools import get_tools

def create_agent():    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)    # temperature=0: 일관된 출력을 위해 창의성 최소화
    
    tools = get_tools()
    
    # LangChain Hub에서 ReAct 프롬프트 템플릿 가져오기
    # ReAct: Reasoning + Acting — 생각하고 행동을 반복하며 답을 찾는 에이전트 패턴
    prompt = hub.pull("hwchase17/react")
    
    # 에이전트 생성: LLM + 툴 + 프롬프트 조합
    agent = create_react_agent(llm, tools, prompt)
    
    # AgentExecutor: 에이전트 실행 루프 관리
    # verbose=True: 에이전트의 추론 과정을 콘솔에 출력
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_agent(keyword: str) -> str:
    agent_executor = create_agent()
    
    # 키워드 기반 뉴스 브리핑 요청
    result = agent_executor.invoke({
        "input": f"""
        '{keyword}' 관련 최신 뉴스를 검색하고 다음 형식으로 브리핑해줘:

        1. 핵심 요약 (3줄)
        2. 주요 뉴스 3개 (제목 + 한줄 요약)
        3. 시사점
        """
    })
    return result["output"]