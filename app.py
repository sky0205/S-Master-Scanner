import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup

# 1. 화면 구성 및 할배 캐릭터 스타일 (완벽 유지)
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36058", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
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
    /* 이평선 전용 스타일 추가 */
    .ma-status-box { background-color: #F1F8E9; border: 2px dashed #43A047; padding: 15px; border-radius: 10px; margin: 10px 0; font-size: 22px; }
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
    except: st.error("⚠️ 데이터 호출 불가")

st.title("🧐 이수할아버지의 냉정 진단기 v36058")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        # 데이터 기간은 장기 이평선을 위해 넉넉히 600일
        start_date = datetime.now() - timedelta(days=600); is_kr = symbol.isdigit()
        now_tz = pytz.timezone('Asia/Seoul') if is_kr else pytz.timezone('US/Eastern')
        now_local = datetime.now(now_tz)

        if is_kr:
            ticker = yf.Ticker(f"{symbol}.KS")
            df = fdr.DataReader(symbol, start=start_date.strftime('%Y-%m-%d'))
            try:
                df_krx = fdr.StockListing('KRX')
                name = df_krx[df_krx['Code'] == symbol]['Name'].values[0]
            except: name = ticker.info.get('shortName', symbol).split(',')[0]
            currency, fmt_p = "원", ",.0f"
            # 실시간 크롤링 (네이버)
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            p = float(soup.select_one(".no_today .blind").text.replace(",", ""))
            v_curr = float(soup.select(".no_info .blind")[3].text.replace(",", ""))
            prev_p = float(df['Close'].iloc[-1])
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date)
            name = ticker.info.get('shortName', symbol)
            currency, fmt_p = "$", ",.2f"
            df_today = ticker.history(period='1d')
            p = float(df_today['Close'].iloc[-1]) if not df_today.empty else float(df['Close'].iloc[-1])
            v_curr = float(df_today['Volume'].iloc[-1]) if not df_today.empty else float(df['Volume'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2])

        if not df.empty:
            # 1. 이동평균선(MA) 계산 및 판독
            df['MA5'] = df['Close'].rolling(5).mean()
            df['MA20'] = df['Close'].rolling(20).mean()
            df['MA60'] = df['Close'].rolling(60).mean()
            df['MA120'] = df['Close'].rolling(120).mean()
            ma5, ma20, ma60, ma120 = df['MA5'].iloc[-1], df['MA20'].iloc[-1], df['MA60'].iloc[-1], df['MA120'].iloc[-1]
            
            if ma5 > ma20 > ma60 > ma120: ma_status, ma_col = "🌈 정배열 (천하무적 진격)", "#2E7D32"
            elif ma5 < ma20 < ma60 < ma120: ma_status, ma_col = "💀 역배열 (지하실 조심)", "#C62828"
            else: ma_status, ma_col = "🌀 혼조세 (성벽 재정비)", "#1565C0"

            # 2. 거래량 강도 (5일 평균 대비)
            v_avg5 = float(df['Volume'].iloc[-6:-1].mean())
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0

            # 3. 4대 지수 계산 (기본틀 엄수)
            df['Std'] = df['Close'].rolling(20).std()
            mid_line, up_b, low_b = df['MA20'].iloc[-1], df['MA20'].iloc[-1] + (df['Std'].iloc[-1] * 2), df['MA20'].iloc[-1] - (df['Std'].iloc[-1] * 2)
            peak_20 = float(df['High'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93
            
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = (100 - (100 / (1 + (gain / (loss + 1e-10))))).iloc[-1]
            h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
            will_val = (h14.iloc[-1] - p) / (h14.iloc[-1] - l14.iloc[-1] + 1e-10) * -100
            macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean(); sig_line = macd.ewm(span=9).mean()
            m_l, s_l, m_p, s_p = macd.iloc[-1], sig_line.iloc[-1], macd.iloc[-2], sig_line.iloc[-2]

            # --- 화면 출력 ---
            st.markdown(f"### 📊 현재주가 및 성벽 전황")
            p_chg = (p - prev_p) / prev_p * 100
            st.markdown(f"""
                <div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>
                    <p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{name} ({symbol})</p>
                    <p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{p:{fmt_p}}{currency} ({p_chg:+.2f}%)</p>
                    <div class='ma-status-box' style='color:{ma_col};'>🚩 <b>이평선:</b> {ma_status} | 5일: {ma5:{fmt_p}} | 20일: {ma20:{fmt_p}}</div>
                </div>
            """, unsafe_allow_html=True)

            # 거래량 (v36056 스타일)
            v_msg = "화력폭발" if v_ratio >= 150 else ("매집시작" if v_ratio >= 100 else "기세부족")
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1;'>📊 거래량: {v_msg} ({v_ratio:.1f}%)</div></div>", unsafe_allow_html=True)

            # 신호등
            if p >= up_b or rsi_val >= 60: sig, col, s_adv = "🟢 매도권 진입", "#388E3C", "● 과열권일세! 수익 챙기시게."
            elif p <= low_b or rsi_val <= 35: sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", "● 바닥권일세. 겁먹지 말고 보따리 푸시게."
            else: sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", "● 눈치싸움 중일세."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            # 4대 지수 정밀 진단 (기본틀 완벽 복원)
            st.divider(); i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_diag = "⚠️ [과열 진입] 수익을 빳빳하게 확정 지으시게." if p >= up_b else ("🏰 [성벽 사수] 중앙선 위 안착 중일세." if p > mid_line else "🏚️ [성문 함락] 절대 칼 뽑지 마시게.")
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            with i2: # RSI
                r_diag = f"● 지수 {rsi_val:.2f}로 {'👺 불지옥' if rsi_val >= 60 else ('🧊 냉골' if rsi_val <= 35 else '중립')} 상태일세."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            with i3: # Williams %R
                w_diag = f"● 지수 {will_val:.2f}로 {'🧨 천장광기' if will_val >= -20 else ('🏳️ 개미항복' if will_val <= -80 else '중간지대')}일세."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            with i4: # MACD
                m_diag = "● 엔진 정회전 중!" if m_l > s_l else "● 엔진 역회전 중!"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 오류: {e}")
