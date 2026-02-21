import streamlit as st
import yfinance as yf
import pandas as pd

# S-Master Scanner 설정
st.set_page_config(page_title="S-Master Scanner", layout="wide")

# 1. 상단 타이틀
st.title("🚀 S-Master 스마트 스캔")
st.markdown("### 정중히 모십니다. 기관의 평단가를 추적하여 '무위험 수익'의 길로 안내합니다.")

# 2. 돋보기 검색 기능 추가
st.subheader("🔍 종목 검색")
search_code = st.text_input("분석할 종목 코드를 입력하세요 (예: 005930, TSLA)", value="005930")

# 입력받은 코드를 yfinance 형식으로 변환
if search_code.isdigit(): # 한국 주식일 경우
    full_code = search_code + ".KS"
else: # 미국 주식일 경우
    full_code = search_code.upper()

# 3. 신호등 표시
col1, col2, col3 = st.columns(3)
col1.error("🔴 매수 적기 (기관 평단가 이하)")
col2.success("🟢 매도 (수익 실현)")
col3.warning("🟡 관망 (보유 유지)")

st.divider()

# 4. 분석 엔진 작동
try:
    ticker = yf.Ticker(full_code)
    name = ticker.info.get('shortName', full_code)
    df = ticker.history(period="1mo")
    
    if not df.empty:
        curr = df['Close'].iloc[-1]
        avg_price = df['Close'].mean()
        diff = ((curr - avg_price) / avg_price) * 100
        
        # 분석 리포트 카드 출력
        st.subheader(f"📊 {name} ({full_code}) 분석 보고서")
        c1, c2, c3 = st.columns(3)
        
        # 국내 주식은 '원', 미국 주식은 '달러($)' 표시
        unit = "$" if ".KS" not in full_code else "원"
        c1.metric("현재가", f"{curr:,.0f}{unit}" if unit=="원" else f"{curr:,.2f}{unit}")
        c2.metric("기관 추정 평단", f"{avg_price:,.0f}{unit}" if unit=="원" else f"{avg_price:,.2f}{unit}")
        c3.metric("괴리율 (Whale DNA)", f"{diff:.2f}%")
        
        st.write(f"🛡️ **심리적 안전장치**: {'용기 있게 페달을 밟을 때입니다.' if curr < avg_price else '브레이크를 잡고 숨죽여야 할 때입니다.'}")
    else:
        st.warning("종목 코드가 올바르지 않거나 데이터를 가져올 수 없습니다.")
except:
    st.error("분석 중 오류가 발생했습니다. 종목 코드를 다시 확인해 주세요.")

# 5. 하단 검색 기록 버튼 (예시)
st.divider()
st.write("🔍 **오늘 검색한 종목**")
if st.button("005930 (삼성전자)"): st.rerun()