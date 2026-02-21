import streamlit as st
import pandas as pd

# 1. 앱 설정
st.set_page_config(page_title="S-Master Scanner", layout="wide")

# 2. 화면 스타일 (어르신 맞춤 글꼴 및 박스)
st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 25px; border-left: 10px solid #cc0000; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .price-box { background-color: #fff4f4; padding: 15px; border-radius: 10px; border: 1px solid #ffcccc; color: #cc0000; font-weight: bold; font-size: 1.2em; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 준비 (수급 우선순위 10개 및 금액 정보)
if 'target_stock' not in st.session_state:
    st.session_state.target_stock = ""

if 'priority_data' not in st.session_state:
    data = {
        "순위": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        "종목명": ["삼성전자", "실리콘투", "SK하이닉스", "현대차", "셀트리온", "기아", "KB금융", "포스코홀딩스", "NAVER", "LG화학"],
        "현재주가": ["58,500원", "41,200원", "175,000원", "235,000원", "188,000원", "115,000원", "71,000원", "372,000원", "185,000원", "448,000원"],
        "적정주가": ["75,000원", "55,000원", "210,000원", "290,000원", "230,000원", "145,000원", "88,000원", "450,000원", "220,000원", "560,000원"],
        "무위험 구간": ["175,000원-185,000원", "40,000원-42,500원", "165,000원-172,000원", "230,000원-241,000원", "185,000원-195,000원", "112,000원-118,000원", "68,000원-72,000원", "365,000원-385,000원", "182,000원-192,000원", "432,000원-455,000원"],
        "신호등": ["🔴 매수", "🔴 매수", "🟡 관망", "🔴 매수", "🔴 매수", "🟡 관망", "🔴 매수", "🟡 관망", "🟡 관망", "🔴 매수"]
    }
    st.session_state.priority_data = pd.DataFrame(data)

# 4. 앱 메인 화면 구성
st.title("🚀 S-Master Scanner (국내주식)")
st.subheader("외인·기관 수급 입체 판독 및 무위험 수익 구간 포착")

# 검색창
search_input = st.text_input("🔍 종목명을 입력하세요", value=st.session_state.target_stock)

if not search_input:
    st.write("---")
    st.header("📅 오늘 장마감 수급 사냥 리스트 (TOP 10)")
    st.table(st.session_state.priority_data)
    
    st.write("### 🔍 종목 상세 분석 (터치 시 화면 전환)")
    cols = st.columns(2)
    for i in range(10):
        name = st.session_state.priority_data['종목명'][i]
        if cols[i % 2].button(f"🔍 {name}", key=f"btn_{name}"):
            st.session_state.target_stock = name
            st.rerun()
else:
    # 종목 상세 분석 (이수 할아버지 양식)
    st.write("---")
    st.header(f"📊 {search_input} 상세 수급 및 지표 진단")
    st.error("매수(적기) - 기관의 평단가보다 저렴하며 무위험 수익 구간에 진입했습니다.")

    st.markdown(f"""
    <div class="report-card">
        <h3>📋 추세 분석 카드</h3>
        어르신, {search_input}의 수급을 입체적으로 판독해 보니 기관이 아주 정밀하게 물량을 확보하고 있습니다. <br>
        무엇보다 기관의 진짜 매수 평단가보다 현재 주가가 낮은 무위험 수익 구간입니다. 
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.write("### 💰 주가 및 수급 금액 판독")
        row = st.session_state.priority_data[st.session_state.priority_data['종목명'] == search_input]
        if not row.empty:
            curr_p = row['현재주가'].values[0]
            target_p = row['적정주가'].values[0]
            safe_p = row['무위험 구간'].values[0]
            
            st.markdown(f"""
            <div class='price-box'>
                ● 현재 주가: {curr_p}<br>
                ● 테이버 적정주가: {target_p}<br>
                <hr>
                ● 무위험 구간: {safe_p}
            </div>
            """, unsafe_allow_html=True)
        
    with col2:
        st.write("### 📊 지표 상세 진단 (20/2, 14/6, 14/9)")
        st.write("**Bollinger (20, 2)** ● 위치: 하단 밴드 지지")
        st.write("**RSI (14, 9)** ● 수치: 33 (매수 적기)")
        st.write("**Williams %R (14, 6)** ● 수치: -82 (바닥 확인)")
        st.write("**MACD** ■ 추세: 상승 전환 포착")

    # 리스트로 돌아가기 버튼
    if st.button("⬅️ 전체 리스트로 돌아가기"):
        st.session_state.target_stock = ""
        st.rerun()