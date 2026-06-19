import streamlit as st
from dotenv import load_dotenv
import sys
import os
from datetime import date
import plotly.graph_objects as go

sys.path.append(os.path.dirname(__file__))
load_dotenv()

from agent import run_agent

def render_news(text):
    items = []
    current = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("제목:"):
            if current.get("title"):
                items.append(current)
            current = {"title": line.replace("제목:", "").strip()}
        elif line.startswith("링크:"):
            url = line.replace("링크:", "").strip()
            if url.startswith("http"):
                current["url"] = url
        elif line.startswith("요약:"):
            current["desc"] = line.replace("요약:", "").strip()
        elif line.startswith("연관이유:"):
            current["desc"] = line.replace("연관이유:", "").strip()
    if current.get("title"):
        items.append(current)

    if not items:
        st.caption("뉴스를 불러오지 못했습니다.")
        return

    for item in items:
        with st.container(border=True):
            col_title, col_btn = st.columns([4, 1])
            with col_title:
                st.markdown(f"**{item.get('title', '')}**")
                if "desc" in item:
                    st.caption(item["desc"])
            with col_btn:
                if "url" in item:
                    st.link_button("🔗 원문", item["url"], use_container_width=True)

st.set_page_config(page_title="AI 뉴스 브리핑", page_icon="📰", layout="wide")

st.markdown("""
    <style>
    .block-container {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# session_state 초기화
if "result" not in st.session_state:
    st.session_state.result = None
if "keyword" not in st.session_state:
    st.session_state.keyword = ""

st.title("📰 AI 뉴스 브리핑 에이전트")
st.caption(f"{date.today().strftime('%Y년 %m월 %d일')} 최신 뉴스를 분석해드립니다.")

# 입력 영역
if st.session_state.result is None:
    col_input, col_btn = st.columns([8, 1])
    with col_input:
        keyword = st.text_input("Type Keyword", placeholder="ex) 반도체, 삼성전자, LLM", label_visibility="collapsed")
    with col_btn:
        clicked = st.button("Search", type="primary", use_container_width=True)

    if clicked and keyword:
        with st.spinner("에이전트가 오늘자 뉴스를 분석 중입니다..."):
            st.session_state.result = run_agent(keyword)
            st.session_state.keyword = keyword
        st.rerun()

else:
    col_input, col_search, col_home = st.columns([6, 1.2, 1])
    with col_input:
        new_keyword = st.text_input("키워드 입력", value=st.session_state.keyword, label_visibility="collapsed")
    with col_search:
        search_clicked = st.button("Search", type="primary", use_container_width=True)
    with col_home:
        home_clicked = st.button("Home", use_container_width=True)

    if home_clicked:
        st.session_state.result = None
        st.session_state.keyword = ""
        st.rerun()

    if search_clicked and new_keyword:
        with st.spinner("에이전트가 오늘자 뉴스를 분석 중입니다..."):
            st.session_state.result = run_agent(new_keyword)
            st.session_state.keyword = new_keyword
        st.rerun()

    result = st.session_state.result

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 📰 주요 뉴스")
        render_news(result["main"])

        st.markdown("### 😊 감성 분석")
        sentiment_text = result["sentiment"]
        pos, neg, neu = 0, 0, 0
        for line in sentiment_text.split("\n"):
            if "긍정:" in line:
                try:
                    pos = int(line.replace("긍정:", "").replace("%", "").strip())
                except:
                    pass
            elif "부정:" in line:
                try:
                    neg = int(line.replace("부정:", "").replace("%", "").strip())
                except:
                    pass
            elif "중립:" in line:
                try:
                    neu = int(line.replace("중립:", "").replace("%", "").strip())
                except:
                    pass

        fig = go.Figure(data=[go.Pie(
            labels=["긍정", "부정", "중립"],
            values=[pos, neg, neu],
            hole=0.5,
            marker_colors=["#4a6fa5", "#e07060", "#a0a0b0"]
        )])
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        with st.container(border=True):
            for line in sentiment_text.split("\n"):
                line = line.strip()
                if line.startswith(("1.", "2.", "3.")):
                    if "[부정]" in line:
                        st.markdown(f"🔴 {line}")
                    elif "[중립]" in line:
                        st.markdown(f"⚪ {line}")
                    elif "[긍정]" in line:
                        st.markdown(f"🟢 {line}")
                    else:
                        st.markdown(f"⚪ {line}")
    with col2:
        st.markdown("### 📋 핵심 요약")
        with st.container(border=True):
            st.markdown(result["summary"])

        st.markdown("### 💡 시사점")
        with st.container(border=True):
            st.markdown(result["insight"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🔗 연관 뉴스")
        render_news(result["related"])

    # 주식 시세
    st.markdown("---")
    st.markdown("### 📈 주식 시세")

    if result.get("stock"):
        stock_text = result["stock"]
        lines = [l.strip() for l in stock_text.split("\n") if l.strip()]
        stocks = {}
        current_company = None
        for line in lines:
            if line.startswith("기업:"):
                current_company = line.replace("기업:", "").strip()
                stocks[current_company] = {}
            elif line.startswith("현재가:") and current_company:
                stocks[current_company]["price"] = line.replace("현재가:", "").strip()
            elif line.startswith("등락:") and current_company:
                stocks[current_company]["change"] = line.replace("등락:", "").strip()
            elif line.startswith("거래량:") and current_company:
                stocks[current_company]["volume"] = line.replace("거래량:", "").strip()
            elif line.startswith("당일고가:") and current_company:
                stocks[current_company]["high"] = line.replace("당일고가:", "").strip()
            elif line.startswith("당일저가:") and current_company:
                stocks[current_company]["low"] = line.replace("당일저가:", "").strip()
            elif line.startswith("52주최고:") and current_company:
                stocks[current_company]["week52_high"] = line.replace("52주최고:", "").strip()
            elif line.startswith("52주최저:") and current_company:
                stocks[current_company]["week52_low"] = line.replace("52주최저:", "").strip()

        num_stocks = len(stocks)
        if num_stocks == 1:
            # 기업 1개면 절반 너비 사용
            stock_cols = st.columns([1, 1])
            render_cols = [stock_cols[0]]
        else:
            stock_cols = st.columns(min(num_stocks, 5))
            render_cols = stock_cols

        for idx, (company, data) in enumerate(stocks.items()):
            if idx >= 5:
                break
            price = data.get("price", "")
            change = data.get("change", "")
            volume = data.get("volume", "")
            is_up = "▲" in change
            is_down = "▼" in change
            color = "green" if is_up else "red" if is_down else "gray"
            with render_cols[idx]:
                with st.container(border=True):
                    st.markdown(f"**{company}**")
                    st.markdown(f"**{price}**")
                    st.markdown(
                        f"<span style='color:{color}'>{change}</span>",
                        unsafe_allow_html=True
                    )
                    if volume and volume != "N/A":
                        st.caption(f"거래량: {volume}")
                    if data.get("high") and data.get("high") != "N/A":
                        st.caption(f"당일 고가: {data['high']} / 저가: {data['low']}")
                    if data.get("week52_high") and data.get("week52_high") != "N/A":
                        st.caption(f"52주 최고: {data['week52_high']} / 최저: {data['week52_low']}")

    st.markdown("---")
    st.markdown("### 🔥 오늘의 이슈")
    render_news(result["issue"])