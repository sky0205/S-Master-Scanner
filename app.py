import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 설정 및 제목
st.set_page_config(page_title="S-Master Scanner", layout="wide")
st.title("🎯 S-Master Scanner: 국장 유망주 사냥기")

# 할아버님이 보셔야 할 국장 핵심 종목 리스트
# (매출이 탄탄하고 수급 유입이 잦은 종목들입니다)
market_watch = {
    '삼성전자': '005930.KS',
    'SK하이닉스': '000660.KS',
    '현대차': '005380.KS',
    '기아': '000270.KS',
    '셀트리온': '068270.KS',
    'KB금융': '105560.KS',
    '삼성바이오': '207940.KS',
    'LG에너지솔루션': '373220.KS'
}


def get_opportunity_analysis(name, symbol):
    try:
        # 최근 60일 데이터 분석
        df = yf.download(symbol, period="60d", progress=False)
        if df.empty: return None

        # 1. 현재가 확인
        curr = int(df['Close'].iloc[-1].iloc[0]) if isinstance(df['Close'].iloc[-1], pd.Series) else int(
            df['Close'].iloc[-1])

        # 2. 세력 평단가 추산 (최근 20일 이동평균)
        avg_cost = int(df['Close'].tail(20).mean())

        # 3. 거래량 분석 (오늘 거래량이 평소보다 터졌는가?)
        avg_volume = df['Volume'].tail(20).mean()
        curr_volume = df['Volume'].iloc[-1]
        vol_ratio = curr_volume / avg_volume

        # 🚦 S-Master 기회 판독 신호
        # 세력 평단가보다 저렴하거나, 거래량이 동반되며 세력 평단을 돌파할 때
        if curr < avg_cost and vol_ratio > 1.2:
            signal = "🔴 매수 적기 (세력 매집중)"
            description = "기관/외인이 밑에서 쓸어담는 중"
        elif curr > avg_cost and vol_ratio > 1.5:
            signal = "🔥 돌파 (추격 가능)"
            description = "세력 평단 뚫고 본격 상승 시작"
        else:
            signal = "🟡 관망 (수급 대기)"
            description = "거래량 폭발 전까지 대기"

        return {
            "종목명": name,
            "현재가": f"{curr:,}원",
            "세력 추정가": f"{avg_cost:,}원",
            "거래 폭발도": f"{vol_ratio:.1f}배",
            "종합 신호": signal,
            "상세 진단": description
        }
    except:
        return None


# 2. 분석 실행 및 결과 나열
results = []
for n, s in market_watch.items():
    res = get_opportunity_analysis(n, s)
    if res: results.append(res)

if results:
    st.markdown("### 🔎 Whale DNA Tracker (국장 핵심 우량주)")
    # 신호가 좋은 순서대로 나열
    df_res = pd.DataFrame(results)
    st.table(df_res)

    st.divider()
    st.info("💡 **매매 팁**: 현재가가 세력 추정가보다 낮으면서 거래 폭발도가 1.0배를 넘는 종목에 주목하세요!")
else:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 새로고침(F5) 해주세요.")