import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup

# 1. 화면 구성 및 할배 캐릭터 스타일 (v36056 정통 양식 복구)
st.set_page_config(page_title="S-Master-Scanner v36059", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-sub-text { font-size: 22px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .signal-box { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .signal-text { font-size: 65px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .trend-card { background-color: #FFFFFF; padding: 30px; border-radius: 20px; border: 5px solid #D32F2F; margin: 20px 0; }
    .trend-title { font-size: 32px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 12px; margin-bottom: 20px; }
    .trend-item { font-size: 23px !important; line-height: 2.0; margin-bottom: 12px; }
    .price-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px; border: 2px solid #CFD8DC; text-align: center; }
    .ind-box { background-color: #FFFFFF; padding: 22px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 550px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .ind-title { font-size: 26px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 10px; margin-bottom: 15px; }
    .ind-diag { font-size: 20px !important; color: #333333 !important; line-height: 1.8; background-color: #FDFDFD; padding: 15px; border-radius: 10px; border-left: 8px solid #D32F2F; }
    .ma-status-box { background-color: #F1F8E9; border: 2px dashed #43A047; padding: 15px; border-radius: 10px; margin: 10px 0; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 글로벌 전황 보고
def display_global_risk():
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info; sp500 = yf.Ticker("^GSPC").fast_info; tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        tnx_val = tnx.last_price; tnx_chg = (tnx_val / tnx.previous_close - 1) * 100
        st.markdown("### 🌍 글로벌 종합 전황")
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp500.last_price:,.2f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")
    except: pass

st.title("🧐 S-Master-Scanner v36059")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 입력 (예: 005930)", "005930")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=600); is_kr = symbol.isdigit()
        if is_kr:
            df = fdr.DataReader(symbol, start=start_date.strftime('%Y-%m-%d'))
            ticker = yf.Ticker(f"{symbol}.KS")
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}); soup = BeautifulSoup(res.text, 'html.parser')
            p = float(soup.select_one(".no_today .blind").text.replace(",", ""))
            v_curr = float(soup.select(".no_info .blind")[3].text.replace(",", ""))
            prev_p = float(df['Close'].iloc[-1]); currency, fmt_p = "원", ",.0f"
            try: df_krx = fdr.StockListing('KRX'); name = df_krx[df_krx['Code'] == symbol]['Name'].values[0]
            except: name = symbol
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date)
            df_today = ticker.history(period='1d')
            p = float(df_today['Close'].iloc[-1]); v_curr = float(df_today['Volume'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2]); name = symbol; currency, fmt_p = "$", ",.2f"

        if not df.empty:
            # [지표 계산]
            df['MA5'] = df['Close'].rolling(5).mean(); df['MA20'] = df['Close'].rolling(20).mean()
            df['MA60'] = df['Close'].rolling(60).mean(); df['MA120'] = df['Close'].rolling(120).mean()
            ma5, ma20, ma60, ma120 = df['MA5'].iloc[-1], df['MA20'].iloc[-1], df['MA60'].iloc[-1], df['MA120'].iloc[-1]
            
            df['Std'] = df['Close'].rolling(20).std()
            up_b, low_b = ma20 + (df['Std'].iloc[-1] * 2), ma20 - (df['Std'].iloc[-1] * 2)
            peak_20 = float(df['High'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93

            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = (100 - (100 / (1 + (gain / (loss + 1e-10))))).iloc[-1]
            h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
            will_val = (h14.iloc[-1] - p) / (h14.iloc[-1] - l14.iloc[-1] + 1e-10) * -100
            macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean(); sig_line = macd.ewm(span=9).mean()
            m_l, s_l = macd.iloc[-1], sig_line.iloc[-1]

            # [전광판 출력]
            p_chg = (p - prev_p) / prev_p * 100
            ma_status = "🌈 정배열" if ma5 > ma20 > ma60 > ma120 else ("💀 역배열" if ma5 < ma20 < ma60 < ma120 else "🌀 혼조세")
            st.markdown(f"""
                <div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>
                    <p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{name} ({symbol})</p>
                    <p style='font-size:32px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{p:{fmt_p}}{currency} ({p_chg:+.2f}%)</p>
                    <div class='ma-status-box'>🚩 <b>이평선:</b> {ma_status} | 5일: {ma5:{fmt_p}} | 20일: {ma20:{fmt_p}}</div>
                </div>
            """, unsafe_allow_html=True)

            # [거래량 판독]
            v_avg5 = float(df['Volume'].iloc[-6:-1].mean()); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            v_msg = "화력폭발" if v_ratio >= 150 else ("매집시작" if v_ratio >= 100 else "기세부족")
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1;'>📊 거래량: {v_msg} ({v_ratio:.1f}%)</div></div>", unsafe_allow_html=True)

            # [수치 카드 (성벽 사수)]
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # [필살 대응 전략]
            if p >= up_b or rsi_val >= 60:
                final_adv = "💰 과열권일세! 욕심부리지 말고 분할 매도로 수익을 빳빳하게 챙기시게."
            elif p <= low_b or rsi_val <= 35:
                final_adv = f"🔥 바닥권 진입했네! **{format(p, fmt_p)}**서 정찰대 보내고 엔진(MACD) 정회전을 기다리시게."
            else:
                final_adv = "🧐 눈치싸움 중일세. 성벽 사수 여부 보며 지표 끝단까지 기다리시게."

            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>1. **성벽 사수:** 현재가 {p:{fmt_p}}원이 방어선 {defense_line:{fmt_p}}원 {'위' if p > defense_line else '아래'}일세.</div>
                <div class='trend-item'>2. **엔진(MACD):** {'정회전' if m_l > s_l else '역회전'} 중이니 시동 소리를 똑똑히 들으시게.</div>
                <div class='trend-item'>3. **온도(RSI):** {rsi_val:.2f}로 {'열기가 오르는 중' if rsi_val > 50 else '식어있는 상태'}일세.</div>
                <hr style='border:1px solid #FFEBEE;'>
                <div class='trend-item' style='color:#D32F2F; font-size:25px !important;'>{final_adv}</div></div>""", unsafe_allow_html=True)

            # [4대 지수 정밀 진단]
            st.divider(); i1, i2, i3, i4 = st.columns(4)
            with i1:
                bb_diag = "⚠️ [과열] 성벽 위일세. 수확(익절) 준비하시게." if p >= up_b else ("🏰 [성벽 사수] 안정적 진격 중일세." if p > ma20 else "🏚️ [성문 함락] 절대 칼 뽑지 마시게.")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2:
                r_diag = f"지수 {rsi_val:.2f}로 {'👺 불지옥' if rsi_val >= 60 else ('🧊 냉골' if rsi_val <= 35 else '중립')}일세."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3:
                w_diag = f"지수 {will_val:.2f}로 {'🧨 천장광기' if will_val >= -20 else ('🏳️ 개미항복' if will_val <= -80 else '중간지대')}일세."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4:
                m_diag = "● 엔진 **정회전**! 기세 좋구먼." if m_l > s_l else "● 엔진 **역회전**! 거꾸로 가는 차일세."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 오류: {e}")
