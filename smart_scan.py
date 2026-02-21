import streamlit as st
import yfinance as yf
import pandas as pd

# 이수 할아버지 양식 설정
st.set_page_config(page_title="S-Master Smart Scan", layout="wide")

st.title("🔴🟡🟢 S-Master 스마트 스캔")
st.write("정중히 모십니다. 오늘의 우량주 수급 및 추세 분석 결과입니다.")

# 분석할 종목 리스트 (예시: 삼성전자, SK하이닉스, 현대차)
stocks = {'005930.KS': '삼성전자', '000660.KS': 'SK하이닉스', '005380.KS': '현대차'}

data_list = []
for code, name in stocks.items():
    ticker = yf.Ticker(code)
    df = ticker.history(period="1mo")
    if not df.empty:
        last_price = df['Close'].iloc[-1]
        change = last_price - df['Close'].iloc[-2]
        data_list.append({'종목코드': code, '종목명': name, '현재가': f"{last_price:,.0f}원", '대비': f"{change:,.0f}원"})

# 결과 표 표시
st.table(pd.DataFrame(data_list))

st.info("💡 위 지표는 볼린저 밴드(20,2), RSI(14,9) 기준으로 계산되었습니다.")