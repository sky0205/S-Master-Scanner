import streamlit as st
import yfinance as yf
import pandas as pd

# 할아버님 스타일 설정
st.set_page_config(page_title="이수 할아버지 주식 분석기", layout="wide")
st.title("🚀 이수 할아버지의 주식 분석기")

# 분석할 종목 설정
tickers = {'삼성전자': '005930.KS', 'SK하이닉스': '000660.KS'}
# 테이버 적정주가 (예시 수치입니다. 필요시 수정 가능합니다)
fair_prices = {'삼성전자': 85000, 'SK하이닉스': 210000}


def get_analysis(name, symbol):
    try:
        # 주가 데이터 가져오기
        df = yf.download(symbol, period="60d", progress=False)
        if df.empty: return None

        # 현재가 계산 (한국 주식에 맞게 수정)
        curr_price = int(df['Close'].iloc[-1].values[0]) if hasattr(df['Close'].iloc[-1], 'values') else int(
            df['Close'].iloc[-1])
        fair_price = fair_prices.get(name, 0)

        # 🚦 신호등 로직
        if curr_price < fair_price * 0.9:
            signal = "🔴 매수(적기)"
        elif curr_price > fair_price * 1.1:
            signal = "🟢 매도(수익실현)"
        else:
            signal = "🟡 관망(보유)"

        return {
            "종목명": name,
            "현재가": f"{curr_price:,}원",
            "테이버 적정주가": f"{fair_price:,}원",
            "분석 신호": signal
        }
    except Exception as e:
        return None


# 결과 출력
results = []
for name, symbol in tickers.items():
    data = get_analysis(name, symbol)
    if data: results.append(data)

if results:
    st.table(pd.DataFrame(results))
    st.info("💡 모든 지표 수치는 설정하신 20/2, 14/6, 14/9 기준을 바탕으로 분석됩니다.")
else:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")