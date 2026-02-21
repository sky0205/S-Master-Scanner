import streamlit as st
import yfinance as yf
import pandas as pd

st.title("🚀 이수 할아버지의 주식 분석기")

# 분석할 종목 (삼성전자, SK하이닉스)
tickers = {'삼성전자': '005930.KS', 'SK하이닉스': '000660.KS'}

def get_analysis(name, symbol):
    try:
        df = yf.download(symbol, period="60d", progress=False)
        close = df['Close']
        curr = float(close.iloc[-1])
        return {"종목명": name, "현재가": f"{int(curr):,}원", "상태": "정상"}
    except: return None

results = [get_analysis(n, s) for n, s in tickers.items() if get_analysis(n, s)]
if results:
    st.table(pd.DataFrame(results))
else:
    st.write("데이터를 불러오는 중입니다...")