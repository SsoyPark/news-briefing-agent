import streamlit as st
from dotenv import load_dotenv
import sys
import os

# app 디렉토리를 모듈 경로에 추가 (agent.py, tools.py import를 위해)
sys.path.append(os.path.dirname(__file__))

# .env 파일에서 API 키 환경변수 로드
load_dotenv()

from agent import run_agent

st.title("📰 AI 뉴스 브리핑 에이전트")
st.caption("키워드를 입력하면 최신 뉴스를 분석해 브리핑해드립니다.")

keyword = st.text_input("키워드 입력", placeholder="예: AI 반도체, 삼성전자, LLM")

if st.button("브리핑 시작"):
    if keyword:
        # 에이전트 실행 중 로딩 스피너 표시
        with st.spinner("에이전트가 뉴스를 분석 중입니다..."):
            result = run_agent(keyword)
        st.markdown("### 브리핑 결과")
        st.markdown(result)
    else:
        st.warning("키워드를 입력해주세요.")