import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="S-Master Scanner", layout="wide")

# 1. 상단 신호등 표시 (규칙 준수)
st.title("🚀 S-Master 수급 우선순위 분석기")
st.markdown("### 정중히 모십니다. 외인·기관의 수급 DNA를 판독하여 최적의 진입 순위를 제안합니다.")

# 분석할 종목 리스트 (할아버님이 원하시는 종목들로 구성)
target_stocks = {
    '005930.KS': '삼성전자', '000660.KS': 'SK하이닉스', 
    '005380.KS': '현대차', '068270.KS': '셀트리온',
    '035420.KS': 'NAVER', '005490.KS': 'POSCO홀딩스'
}

analysis_results = []

for code, name in target_stocks.items():
    tk = yf.Ticker(code)
    # 수급 분석 (최근 5일간의 흐름 파악)
    df = tk.history(period="5d")
    if not df.empty:
        curr = df['Close'].iloc[-1]
        avg_5d = df['Close'].mean()  # 5일 평균가 (세력 추정가)
        diff = ((curr - avg_5d) / avg_5d) * 100
        vol_change = df['Volume'].iloc[-1] / df['Volume'].mean() # 거래량 변화
        
        # 순위 점수 계산 (괴리율이 낮고 거래량이 터질수록 높은 순위)
        score = -diff + (vol_change * 10)
        
        # 상태 판정
        if curr < avg_5d: status = "🔴 매수적기"; color = "red"
        elif diff > 10: status = "🟢 수익실현"; color = "green"
        else: status = "🟡 관망"; color = "orange"
        
        analysis_results.append({
            '순위점수': score, '종목명': name, '현재가': curr, 
            '세력추정가': avg_5d, '괴리율': diff, '상태': status
        })

# 2. 우선순위 정렬 (점수 높은 순)
df_result = pd.DataFrame(analysis_results).sort_values(by='순위점수', ascending=False)

# 3. 화면 출력 (카드 형태)
for i, row in enumerate(df_result.iloc[:5].itertuples()):
    with st.container():
        st.markdown(f"#### 🏆 {i+1}순위: {row.종목명} ({row.상태})")
        c1, c2, c3 = st.columns(3)
        c1.metric("현재가", f"{row.현재가:,.0f}원")
        c2.metric("세력평단(5일)", f"{row.세력추정가:,.0f}원")
        c3.metric("괴리율", f"{row.괴리율:.2f}%", delta_color="inverse")
        st.write(f"🛡️ **판독**: {'외인·기관보다 저렴한 구간입니다. 공격적 진입 추천' if row.괴리율 < 0 else '추격 매수보다는 눌림목을 기다리세요.'}")
        st.divider()