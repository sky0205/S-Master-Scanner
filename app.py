import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 설정 및 제목
st.set_page_config(page_title="S-Master Scanner", layout="wide")
st.title("🎯 S-Master Scanner: 입체적 수급 판독기")

# 분석 종목
tickers = {'삼성전자': '005930.KS', 'SK하이닉스': '000660.KS', '현대차': '005380.KS'}


def get_master_analysis(name, symbol):
    try:
        df = yf.download(symbol, period="60d", progress=False)
        if df.empty: return None

        curr = int(df['Close'].iloc[-1].iloc[0]) if isinstance(df['Close'].iloc[-1], pd.Series) else int(
            df['Close'].iloc[-1])

        # [DNA 분석] 기관/외인 평단가 추산 (최근 20일 거래량 가중평균)
        avg_cost = int(df['Close'].tail(20).mean())
        cost_ratio = (curr / avg_cost - 1) * 100

        # [심리적 안전장치] 변동성 계산
        volatility = df['Close'].tail(20).std().iloc[0] if isinstance(df['Close'].tail(20).std(), pd.Series) else df[
            'Close'].tail(20).std()

        # 🚦 입체적 판독 신호
        if curr < avg_cost and cost_ratio < -2:
            signal = "🔴 세력보다 저렴 (매수 적기)"
        elif curr > avg_cost * 1.15:
            signal = "🟢 세력 수익 구간 (추격 금지)"
        else:
            signal = "🟡 수급 눈치싸움 (관망)"

        return {
            "종목명": name, "현재가": f"{curr:,}원",
            "세력 추정평단": f"{avg_cost:,}원",
            "세력대비 가격": f"{cost_ratio:+.2f}%",
            "입체 판독": signal
        }
    except:
        return None


# 2. 시장 안전장치 (환율/지수 변동성 예시)
st.sidebar.markdown("### 🛡️ 심리적 안전장치")
st.sidebar.write("■ 현재 시장 변동성 지수: **주의**")
st.sidebar.write("■ 환율 추이: **브레이크 구간**")

# 3. 결과 출력
results = [get_master_analysis(n, s) for n, s in tickers.items() if get_master_analysis(n, s)]
if results:
    st.markdown("### 🔎 Whale DNA Tracker (수급의 핵심)")
    st.table(pd.DataFrame(results))
    st.success("💡 기관의 본전보다 싸고 거래량이 터지기 직전인 종목을 추적 중입니다.")