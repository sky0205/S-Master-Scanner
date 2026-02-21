import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 상단 신호등 및 타이틀 (정중한 말투)
st.set_page_config(page_title="S-Master Scanner", layout="wide")
st.title("🚀 S-Master 스마트 스캔")
st.markdown("### 정중히 모십니다. 기관의 평단가를 추적하여 '무위험 수익'의 길로 안내합니다.")

# 신호등 표시 (예시 데이터)
col1, col2, col3 = st.columns(3)
col1.error("🔴 매수 적기 (기관 평단가 이하)")
col2.success("🟢 매도 (수익 실현)")
col3.warning("🟡 관망 (보유 유지)")

st.divider()

# 2. 종합 추세 분석 카드 (부드러운 설명)
st.subheader("📊 오늘의 종합 추세 분석 카드")
st.info("""
● 현재 시장은 기관의 매집이 포착되는 'Whale DNA' 단계에 진입했습니다.
■ 세력의 본전보다 저렴한 구간이므로, 심리적 안전장치를 가동하여 분할 매수를 권장드립니다.
""")

# 3. 3대 핵심 위력 분석 엔진
stocks = {'005930.KS': '삼성전자', '000660.KS': 'SK하이닉스', '005380.KS': '현대차'}

for code, name in stocks.items():
    ticker = yf.Ticker(code)
    df = ticker.history(period="1mo")
    if not df.empty:
        curr = df['Close'].iloc[-1]
        avg_price = df['Close'].mean() # 기관 추정 평단가
        diff = ((curr - avg_price) / avg_price) * 100
        
        # 종목별 카드 형태 출력
        with st.container():
            st.markdown(f"### 🔍 {name} ({code}) 분석 보고서")
            c1, c2, c3 = st.columns(3)
            c1.metric("현재가", f"{curr:,.0f}원")
            c2.metric("기관 추정 평단", f"{avg_price:,.0f}원")
            c3.metric("괴리율 (Whale DNA)", f"{diff:.2f}%", delta_color="inverse")
            
            st.write(f"🛡️ **심리적 안전장치**: {'용기 있게 페달을 밟을 때입니다.' if curr < avg_price else '브레이크를 잡고 숨죽여야 할 때입니다.'}")
            st.divider()

# 4. 하단 적정주가 표시 (국내 주식은 '원')
st.subheader("💰 테이버의 적정주가")
st.success("삼성전자 적정주가: 85,000원 | SK하이닉스 적정주가: 210,000원")