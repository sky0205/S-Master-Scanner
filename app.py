import streamlit as st
import pandas as pd

# 1. 상단 신호등 설정
st.title("🚀 S-Master Scanner")
col1, col2, col3 = st.columns(3)
with col1: st.success("🔴 매수(적기)")
with col2: st.warning("🟡 관망(보유)")
with col3: st.error("🟢 매도(수익실현)")

# 2. 종합 추세 분석 카드
st.info("### 📋 추세 분석 카드\n현재 시장은 기관과 외인의 수급이 교차하는 지점입니다. 분할 매수로 대응하십시오.")

# 3. 나열형 지표 리스트 (볼린저, RSI, 윌리엄 등)
st.subheader("🎯 실시간 종목 분석 리스트")
data = {
    "종목명": ["삼성전자", "SK하이닉스", "현대차"],
    "볼린저": ["중단 위치", "상단 돌파", "하단 지지"],
    "RSI/윌리엄": ["14/6", "14/9", "20/2"],
    "MACD": ["▲ 상승", "▼ 하락", "▲ 상승"]
}
df = pd.DataFrame(data)
st.table(df) # 할아버님이 원하신 나열형 표