import streamlit as st
import yfinance as yf
import pandas as pd

# 앱 설정 및 제목
st.set_page_config(page_title="S-Master Scanner", layout="wide")
st.title("🚀 S-Master Scanner: 실시간 수급 분석")

# 1. 상단 신호등 (할아버지 양식)
col1, col2, col3 = st.columns(3)
with col1: st.success("🔴 매수(적기)")
with col2: st.warning("🟡 관망(보유)")
with col3: st.error("🟢 매도(수익실현)")

# 2. 분석할 종목 설정 (국내 대표 종목 예시)
# TIP: 나중에는 여기에 2,500개 리스트를 연결할 수 있습니다.
tickers = {'삼성전자': '005930.KS', 'SK하이닉스': '000660.KS', '현대차': '005380.KS', 'LG에너지솔루션': '373220.KS'}


def get_analysis(name, symbol):
    df = yf.download(symbol, period="60d", interval="1d", progress=False)
    current_price = df['Close'].iloc[-1]

    # 볼린저 밴드 (20, 2)
    ma20 = df['Close'].rolling(window=20).mean()
    std20 = df['Close'].rolling(window=20).std()
    upper_band = ma20 + (std20 * 2)
    lower_band = ma20 - (std20 * 2)

    # RSI (14, 9)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # 윌리엄 %R (14, 6)
    high_14 = df['High'].rolling(window=14).max()
    low_14 = df['Low'].rolling(window=14).min()
    w_r = (high_14 - df['Close']) / (high_14 - low_14) * -100

    # 종합 진단
    status = "🟡 관망"
    if current_price < lower_band.iloc[-1] and rsi.iloc[-1] < 30:
        status = "🔴 매수"
    elif current_price > upper_band.iloc[-1] or rsi.iloc[-1] > 70:
        status = "🟢 매도"

    return {
        "종목명": name,
        "현재가": f"{int(current_price):,}원",
        "볼린저": "하단 돌파" if current_price < lower_band.iloc[-1] else "정상",
        "RSI": f"{rsi.iloc[-1]:.1f}",
        "윌리엄": f"{w_r.iloc[-1]:.1f}",
        "진단": status
    }


# 3. 데이터 나열
results = [get_analysis(name, sym) for name, sym in tickers.items()]
st.table(pd.DataFrame(results))

# 4. 하단 검색 기능 (🔍 버튼 대용)
st.divider()
target_code = st.text_input("🔍 종목 코드를 입력하세요 (예: 005930)", "")
if target_code:
    st.write(f"입력하신 {target_code} 종목을 정밀 분석 중입니다...")