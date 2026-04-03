import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup

# 1. 화면 구성 및 할배 캐릭터 스타일
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36068", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-main-text { font-size: 32px !important; color: #0D47A1 !important; margin-bottom: 10px; }
    .vol-sub-text { font-size: 20px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-text { font-size: 65px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .trend-item { font-size: 23px !important; line-height: 2.0; margin-bottom: 12px; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 520px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    .ma-box { background-color: #F1F8E9; border: 2px dashed #43A047; padding: 15px; border-radius: 10px; margin-top: 10px; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        tnx_val = tnx.last_price; tnx_chg = (tnx_val / tnx.previous_close - 1) * 100
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp500.last_price:,.2f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")
        
        if tnx_val >= 4.5: adv = "🚨 **[금리 발작: 비상]** 국채 금리가 4.5%를 넘어섰네! 기술주 성벽 무너질 수 있으니 진격을 멈추시게."
        elif n_chg > 0.5 and tnx_chg < 0: adv = "🔥 **[골디락스 진입]** 지수는 오르고 금리는 내리니 기세 타시게."
        else: adv = "🧐 **[눈치싸움 중]** 세력들이 간 보고 있구먼. 섣부른 판단은 독이네."
        st.info(f"🧐 이수 할배의 글로벌 판독: {adv}")
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36068")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=600); is_kr = symbol.isdigit()
        now_tz = pytz.timezone('Asia/Seoul') if is_kr else pytz.timezone('US/Eastern')
        now_local = datetime.now(now_tz)

        if is_kr:
            ticker = yf.Ticker(f"{symbol}.KS")
            df = fdr.DataReader(symbol, start=start_date.strftime('%Y-%m-%d'))
            try:
                df_krx = fdr.StockListing('KRX')
                name = df_krx[df_krx['Code'] == symbol]['Name'].values[0]
            except: name = symbol
            currency, fmt_p = "원", ",.0f"
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date)
            name = symbol; currency, fmt_p = "$", ",.2f"

        if not df.empty:
            df = df.ffill().dropna()
            
            if is_kr:
                url = f"https://finance.naver.com/item/main.naver?code={symbol}"
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(res.text, 'html.parser')
                p = float(soup.select_one(".no_today .blind").text.replace(",", ""))
                v_curr = float(soup.select(".no_info .blind")[3].text.replace(",", ""))
            else:
                df_today = ticker.history(period='1d')
                p = float(df_today['Close'].iloc[-1]) if not df_today.empty else float(df['Close'].iloc[-1])
                v_curr = float(df_today['Volume'].iloc[-1]) if not df_today.empty else float(df['Volume'].iloc[-1])

            # [수선] 수치 단일화: 거래율(v_ratio) 계산
            v_avg5 = float(df['Volume'].iloc[-6:-1].mean())
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            
            # [수선] 화력 중심 표현 교정
            if v_ratio < 50: v_status, v_msg = "📉 화력빈약", f"현재 화력이 {v_ratio:.1f}%로 아직은 안개뿐이니, 아군 화력을 더 기다리시게."
            elif v_ratio < 100: v_status, v_msg = "🧐 화력대기", f"현재 화력 {v_ratio:.1f}%로 평균치를 향해 아군 화력이 차오르고 있네."
            else: v_status, v_msg = "🔥 화력충만", f"화력이 {v_ratio:.1f}%로 기세가 아주 충만하네!"

            prev_p = float(df['Close'].iloc[-1])
            if is_kr and p == prev_p: prev_p = float(df['Close'].iloc[-2])
            p_diff, p_chg = p - prev_p, (p - prev_p) / prev_p * 100

            # [수선] 지표 계산 로직 완벽 복구
            df['MA5'] = df['Close'].rolling(5).mean(); df['MA20'] = df['Close'].rolling(20).mean()
            ma5, ma5_p, ma20 = df['MA5'].iloc[-1], df['MA5'].iloc[-2], df['MA20'].iloc[-1]
            std = df['Close'].rolling(20).std().iloc[-1]; up_b, low_b = ma20 + (2 * std), ma20 - (2 * std)
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = 100 - (100 / (1 + (gain / (loss + 1e-10)).iloc[-1]))
            exp1 = df['Close'].ewm(span=12, adjust=False).mean(); exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2; signal = macd.ewm(span=9, adjust=False).mean()
            m_l, s_l = macd.iloc[-1], signal.iloc[-1]
            h14 = df['High'].rolling(14).max().iloc[-1]; l14 = df['Low'].rolling(14).min().iloc[-1]
            will_val = (h14 - p) / (h14 - l14) * -100 if (h14 - l14) != 0 else -50
            defense_line = float(df['High'].iloc[-21:-1].max()) * 0.93

            ma_status = "🌈 정배열" if ma5 > ma20 else "🌀 혼조세"
            ma_col = "#2E7D32" if ma5 > ma20 else "#1565C0"

            # 전광판 출력
            st.markdown("### 📊 현재주가 및 이동평균 성벽")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"""<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>
                <p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{name} ({symbol})</p>
                <p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p>
                <div class='ma-box' style='color:{ma_col};'>🚩 <b>이평선:</b> {ma_status} | 5일: {ma5:{fmt_p}} | 20일: {ma20:{fmt_p}}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown(f"""<div class='vol-box'><div class='vol-main-text'>📊 거래량 전황: {v_status} ({v_ratio:.1f}%)</div>
                <div class='vol-sub-text'>✅ {v_msg}</div></div>""", unsafe_allow_html=True)

            # [수선] 필살 전략 및 결론 (image_a6f48c.jpg 로직 완벽 복구)
            ma_adv = f"5일선({format(ma5, fmt_p)}) 위에서 기세가 좋네." if p > ma5 else f"5일선({format(ma5, fmt_p)}) 밑으로 고개 숙였어."
            adv1 = f"1. **이평 성벽:** {ma_status} 상태이며, {ma_adv}"
            adv2 = f"2. **성벽 사수:** 현재 주가가 성벽({format(defense_line, fmt_p)}) {'아래' if p < defense_line else '위'}일세."
            adv3 = f"3. **엔진(MACD):** {'정회전' if m_l > s_l else '역회전'} 중일세!"

            if p >= up_b or rsi_val >= 60:
                final_adv = f"🚨 **[최종 결론]** {v_status}! 성벽({format(defense_line, fmt_p)}) 위이나 과열권일세. **분할 익절**하시게!"
                sig, col = "🟢 매도권 진입", "#388E3C"
            elif p <= (low_b * 1.02):
                final_adv = f"🔥 **[최종 결론]** {v_status}! 바닥권 탈환 중이네. **정찰대 투입** 고려하시게."
                sig, col = "🔴 매수권 진입", "#D32F2F"
            else:
                final_adv = f"📈 **[최종 결론]** {v_status}! {ma_status} 유지하며 추세 관망하시게."
                sig, col = "🟡 관망 및 대기", "#FBC02D"

            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p></div>", unsafe_allow_html=True)

            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>{adv1}</div><div class='trend-item'>{adv2}</div><div class='trend-item'>{adv3}</div>
                <hr style='border:1px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div></div>""", unsafe_allow_html=True)

            # [수선] 하단 상세 지표 (image_a6f48c.jpg 스타일 완벽 복구)
            st.divider(); i1, i2, i3, i4 = st.columns(4)
            with i1:
                bb_diag = "⚠️ **[과열 진입]** 온도가 높네. 수익 확정하시게." if p >= up_b or rsi_val >= 60 else ("🏰 **[성벽 사수]** 안정적 진격 중." if p > ma20 else "🏚️ **[성문 함락]** 절대 관망!")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2:
                r_diag = f"지수 {rsi_val:.2f}로 {'👺 불지옥' if rsi_val >= 60 else ('🧊 냉골' if rsi_val <= 35 else '중립')}일세."
                st.markdown(f"""<div class='ind-box'><p class='ind-title'>RSI (온도)</p>
                    <p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p>
                    <p class='ind-diag'>{r_diag}</p></div>""", unsafe_allow_html=True)
            with i3:
                w_diag = f"지수 {will_val:.2f}로 {'🧨 천정' if will_val >= -20 else ('🏳️ 개미항복' if will_val <= -80 else '중간지대')}일세."
                st.markdown(f"""<div class='ind-box'><p class='ind-title'>Williams %R</p>
                    <p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p>
                    <p class='ind-diag'>{w_diag}</p></div>""", unsafe_allow_html=True)
            with i4:
                m_diag = "● 엔진 **정회전**!" if m_l > s_l else "● 엔진 **역회전**!"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류: {e}")
