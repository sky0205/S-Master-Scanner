import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup

# 1. 화면 구성 및 할배 캐릭터 스타일 (이미지 양식 완벽 재현)
st.set_page_config(page_title="S-Master-Scanner v36062", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ECEFF1; } 
    * { font-weight: bold !important; font-family: 'Nanum Gothic', sans-serif; color: #263238; }
    .vol-box { background-color: #E3F2FD; padding: 25px; border-radius: 15px; border: 4px solid #1E88E5; margin-bottom: 20px; }
    .vol-sub-text { font-size: 22px !important; color: #1565C0 !important; line-height: 1.6; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border-left: 6px solid #1E88E5; }
    .signal-box { padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 25px; box-shadow: 2px 2px 15px rgba(0,0,0,0.1); }
    .signal-text { font-size: 85px !important; font-weight: 900 !important; color: #FFFFFF !important; }
    .price-card { background-color: #FFFFFF; padding: 30px; border-radius: 15px; border: 2.5px solid #CFD8DC; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .trend-card { background-color: #FFFFFF; padding: 35px; border-radius: 20px; border: 5px solid #D32F2F; margin: 25px 0; }
    .trend-title { font-size: 35px !important; color: #D32F2F !important; border-bottom: 3px solid #FFEBEE; padding-bottom: 15px; margin-bottom: 25px; }
    .trend-item { font-size: 24px !important; line-height: 2.2; margin-bottom: 15px; }
    .ind-box { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 2.5px solid #90A4AE; min-height: 550px; margin-bottom: 20px; }
    .ind-title { font-size: 28px !important; color: #1976D2 !important; border-bottom: 2px solid #EEEEEE; padding-bottom: 12px; margin-bottom: 18px; }
    .ind-diag { font-size: 21px !important; color: #333333 !important; line-height: 1.9; background-color: #FDFDFD; padding: 18px; border-radius: 12px; border-left: 10px solid #D32F2F; }
    .ma-status-box { background-color: #F1F8E9; border: 2px dashed #43A047; padding: 18px; border-radius: 12px; margin: 15px 0; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧐 S-Master-Scanner v36062")

symbol = st.text_input("📊 분석할 종목번호 입력 (예: 005930)", "000100")

if symbol:
    try:
        start_date = datetime.now() - timedelta(days=600); is_kr = symbol.isdigit()
        if is_kr:
            df = fdr.DataReader(symbol, start=start_date.strftime('%Y-%m-%d'))
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}); soup = BeautifulSoup(res.text, 'html.parser')
            p = float(soup.select_one(".no_today .blind").text.replace(",", ""))
            v_curr = float(soup.select(".no_info .blind")[3].text.replace(",", ""))
            prev_p = float(df['Close'].iloc[-1]); currency, fmt_p = "원", ",.0f"
            try: df_krx = fdr.StockListing('KRX'); name = df_krx[df_krx['Code'] == symbol]['Name'].values[0]
            except: name = symbol
        else:
            ticker = yf.Ticker(symbol); df = ticker.history(start=start_date)
            p = float(df['Close'].iloc[-1]); v_curr = float(df['Volume'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2]); name = symbol; currency, fmt_p = "$", ",.2f"

        if not df.empty:
            # [지표 계산]
            df['MA5'] = df['Close'].rolling(5).mean(); df['MA20'] = df['Close'].rolling(20).mean()
            df['MA60'] = df['Close'].rolling(60).mean(); df['MA120'] = df['Close'].rolling(120).mean()
            ma5, ma20, ma60, ma120 = df['MA5'].iloc[-1], df['MA20'].iloc[-1], df['MA60'].iloc[-1], df['MA120'].iloc[-1]
            df['Std'] = df['Close'].rolling(20).std()
            up_b, low_b = ma20 + (df['Std'].iloc[-1] * 2), ma20 - (df['Std'].iloc[-1] * 2)
            peak_20 = float(df['High'].iloc[-21:-1].max()); defense_line = peak_20 * 0.93

            # [1. 상단 현재가 정보]
            p_chg = (p - prev_p) / prev_p * 100
            ma_status = "🌈 정배열" if ma5 > ma20 > ma60 > ma120 else ("💀 역배열" if ma5 < ma20 < ma60 < ma120 else "🌀 혼조세")
            st.markdown(f"""
                <div style='background-color:#f8f9fa; padding:25px; border-radius:15px; border-left:12px solid #1565C0;'>
                    <p style='font-size:40px; color:#1565C0; font-weight:bold; margin:0;'>{name} ({symbol})</p>
                    <p style='font-size:36px; color:#FF4B4B; font-weight:bold; margin:15px 0 0 0;'>{p:{fmt_p}}{currency} ({p_chg:+.2f}%)</p>
                    <div class='ma-status-box'>🚩 <b>이평선:</b> {ma_status} | 5일: {ma5:{fmt_p}} | 20일: {ma20:{fmt_p}}</div>
                </div>
            """, unsafe_allow_html=True)

            # [2. 거래량 전황]
            v_avg5 = float(df['Volume'].iloc[-6:-1].mean()); v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            v_msg = "아군 화력을 더 기다리시게." if v_ratio < 100 else "추세를 타시게!"
            st.markdown(f"<div class='vol-box'><div style='font-size:32px; font-weight:bold; color:#0D47A1;'>📊 거래량 전황: {'기세부족' if v_ratio<100 else '매집중'} ({v_ratio:.1f}%)</div><div class='vol-sub-text'>✅ 현재 거래율 {v_ratio:.1f}%로 {v_msg}</div></div>", unsafe_allow_html=True)

            # [3. 대형 신호등]
            if p >= (up_b * 0.98): sig, col, s_adv = "🟢 매도권 진입", "#388E3C", "● 👺 불지옥 문턱일세! 익절하시게."
            elif p <= (low_b * 1.02): sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", "● 🧊 바닥권일세. 보따리 푸시게."
            else: sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", "● 눈치싸움 중일세."
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:24px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            # [4. ★수치 카드 복구 핵심 구역★]
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p style='font-size:22px;'>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:45px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p style='font-size:22px;'>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:45px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p style='font-size:22px;'>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:45px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # [5. 대응 전략]
            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div><div class='trend-item'>1. **성벽 사수:** 현재가 {p:{fmt_p}}원, 성벽 {defense_line:{fmt_p}}원 대비 {'위' if p>defense_line else '아래'}일세.</div><hr><div class='trend-item' style='color:#D32F2F; font-size:28px !important;'>🎯 **최종 결론:** {'분할 수확!' if p>=up_b else '매복 관망!'}</div></div>""", unsafe_allow_html=True)

            # [6. 4대 지수 정밀 진단]
            delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi_val = (100 - (100 / (1 + (gain / (loss + 1e-10))))).iloc[-1]
            h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
            will_val = (h14.iloc[-1] - p) / (h14.iloc[-1] - l14.iloc[-1] + 1e-10) * -100
            macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean(); sig_line = macd.ewm(span=9).mean()
            m_l, s_l = macd.iloc[-1], sig_line.iloc[-1]

            st.divider(); i1, i2, i3, i4 = st.columns(4)
            with i1: st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger</p><p class='ind-diag'>{'⚠️ 과열' if p>=up_b else '🏰 성벽사수'}</p></div>", unsafe_allow_html=True)
            with i2: st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI</p><p style='font-size:45px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{'👺 불지옥' if rsi_val>=60 else '중립'}</p></div>", unsafe_allow_html=True)
            with i3: st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:45px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{'🧨 천장' if will_val>=-20 else '중간'}</p></div>", unsafe_allow_html=True)
            with i4: st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD</p><p class='ind-diag'>{'● 정회전' if m_l>s_l else '● 역회전'}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 오류: {e}")
