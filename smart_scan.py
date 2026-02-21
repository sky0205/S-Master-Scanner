import streamlit as st
import pandas as pd

# 1. 앱 기본 설정
st.set_page_config(page_title="S-Master Scanner (국내주식 전용)", layout="wide")

# 2. 스타일 설정 (어르신 보기 편하시게 글자 크기 조정)
st.markdown("""
    <style>
    .priority-text { font-size: 1.2em; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #f8f9fa; }
    .report-card { background-color: #ffffff; padding: 25px; border: 2px solid #e0e0e0; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로직: 장마감 뒤 수급 우선순위 (국내 10개 품목 예시)
# 실제 운영 시에는 국내 주식 시세 API와 연동됩니다.
data = {
    "순위": [f"{i}순위" for i in range(1, 11)],
    "종목명": ["삼성전자", "실리콘투", "SK하이닉스", "현대차", "LG에너지솔루션", "셀트리온", "기아", "KB금융", "NAVER", "신한지주"],
    "외인/기관 수급": ["기관 광기 매집", "외인/기관 동반매수", "기관 매집 중", "기관 순매수", "외인 매집", "기관 매수세 유입", "외인/기관 쌍끌이", "기관 본전 사수", "수급 개선 중", "기관 집중 매수"],
    "수급 DNA (평단대비)": ["기관 본전 아래", "세력 매집 구간", "평단가 근처", "기관 평단 아래", "매집 초기", "저평가 구간", "기관 본전 아래", "안전 구간", "바닥 다지기", "매수 우위"],
    "신호등": ["🔴 매수", "🔴 매수", "🟡 관망", "🔴 매수", "🟡 관망", "🔴 매수", "🔴 매수", "🟡 관망", "🟡 관망", "🔴 매수"]
}
df = pd.DataFrame(data)

# 4. 앱 메인 화면
st.title("🚀 S-Master Scanner (국내주식)")
st.subheader("국내 시장 전 종목 수급 저격 및 입체 판독")

# 5. 종목 검색 기능
search_query = st.text_input("🔍 분석하고 싶은 종목명 또는 코드를 입력하세요", key="search_input")

if not search_query:
    st.write("---")
    st.header("📅 오늘 장마감 수급 사냥 리스트 (TOP 10)")
    
    # 10개 품목 테이블 출력
    st.table(df)
    
    st.write("### 🔍 바로가기 버튼")
    # 10개 품목을 버튼으로 나열 (터치 시 즉시 전환)
    for i in range(0, 10, 2):
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🔍 {df['종목명'][i]}"):
                st.session_state.search_input = df['종목명'][i]
                st.rerun()
        with col2:
            if st.button(f"🔍 {df['종목명'][i+1]}"):
                st.session_state.search_input = df['종목명'][i+1]
                st.rerun()

else:
    # 6. 종목 상세 분석 화면 (이수 할아버지 양식 적용)
    st.write("---")
    st.header(f"📊 {search_query} 상세 수급 및 지표 진단")
    
    # 상단 신호등
    st.success("🔴 매수(적기) - 기관의 평단가보다 저렴하며 거래량이 터지기 직전입니다.")
    
    # 추세 분석 카드
    st.markdown(f"""
    <div class="report-card">
        <h3>📋 추세 분석 카드</h3>
        어르신, 지금 {search_query}의 수급을 입체적으로 판독해 보니 기관이 소리 없이 물량을 쓸어담고 있습니다.<br>
        외인과 기관의 매수 현황이 매우 긍정적이며, 무엇보다 그들의 <b>'진짜 매수 평단가'</b>보다 현재 주가가 낮아 
        무위험 수익을 노려볼 만한 아주 좋은 사냥감입니다. 용기 있게 페달을 밟으셔도 좋을 구간입니다.
    </div>
    """, unsafe_allow_html=True)

    # 지표 상세 진단 (20/2, 14/6, 14/9)
    st.write("")
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### 💰 테이버의 적정주가")
        st.info("국내 주식: 현재가 대비 +15% 저평가 (원화 계산)")

    with col_b:
        st.write("### 📊 지표 상세 진단 (설정치: 20/2, 14/6, 14/9)")
        st.write("**Bollinger (20, 2)** ● 위치: 하단 밴드에서 기관 매집 지지 중")
        st.write("**RSI (14, 9)** ● 상세 수치: 34 (안전 구간)")
        st.write("**Williams %R (14, 6)** ● 상세 수치: -82 (사냥 적기)")
        st.write("**MACD** ■ 추세: 하락 힘 약화 및 **상승(▲)** 전환 포착")

    if st.button("⬅️ 전체 리스트로 돌아가기"):
        st.session_state.search_input = ""
        st.rerun()