import streamlit as st
import yfinance as yf
import pandas as pd

1. 앱 설정
st.set_page_config(page_title="S-Master Scanner", layout="wide")
st.title("🚀 S-Master Scanner")

2. 신호등 표시
col1, col2, col3 = st.columns(3)
with col1: st.success("🔴 매수(적기)")
with col2: st.warning("🟡 관망(보유)")
with col3: st.error("🟢 매도(수익실현)")

3. 분석 종목
tickers = {'삼성전자': '005930.KS', 'SK하이닉스': '000660.KS', '현대차': '005380.KS'}

def get_analysis(name, symbol):
try:
df = yf.download(symbol, period="60d", interval="1d", progress=False)
if df.empty: return None
close = df['Close'].iloc[:, 0] if len(df['Close'].shape) > 1 else df['Close']
ma20 = close.rolling(window=20).mean()
std20 = close.rolling(window=20).std()
upper_band = ma20 + (std20 * 2)
lower_band = ma20 - (std20 * 2)
delta = close.diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rsi = 100 - (100 / (1 + (gain / loss)))
curr = float(close.iloc[-1])
last_rsi = float(rsi.iloc[-1])
status = "🟡 관망"
if curr < lower_band.iloc[-1] and last_rsi < 35: status = "🔴 매수"
elif curr > upper_band.iloc[-1] or last_rsi > 65: status = "🟢 매도"
return {"종목명": name, "현재가": f"{int(curr):,}원", "볼린저": "하단 지지" if curr < lower_band.iloc[-1] else "정상", "RSI": f"{last_rsi:.1f}", "진단": status}
except: return None

4. 출력
results = []
for name, sym in tickers.items():
res = get_analysis(name, sym)
if res: results.append(res)
if results: st.table(pd.DataFrame(results))
else: st.write("데이터 분석 중...")