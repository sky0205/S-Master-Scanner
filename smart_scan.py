import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup

# 1. 화면 구성 및 할배 캐릭터 스타일 (엄수)
st.set_page_config(page_title="이수할아버지의 냉정 진단기 v36056", layout="wide")
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
    </style>
    """, unsafe_allow_html=True)

def display_global_risk():
    st.markdown("### 🌍 글로벌 시장 및 국채 종합 전황")
    try:
        nasdaq = yf.Ticker("^IXIC").fast_info
        sp500 = yf.Ticker("^GSPC").fast_info
        tnx = yf.Ticker("^TNX").fast_info 
        n_chg = (nasdaq.last_price / nasdaq.previous_close - 1) * 100
        tnx_val = tnx.last_price
        tnx_chg = (tnx_val / tnx.previous_close - 1) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("나스닥 (NASDAQ)", f"{nasdaq.last_price:,.2f}", f"{n_chg:.2f}%")
        c2.metric("S&P 500 (SPX)", f"{sp500.last_price:,.2f}", f"{(sp500.last_price/sp500.previous_close-1)*100:.2f}%")
        c3.metric("미 국채 10년물 (TNX)", f"{tnx_val:.3f}%", f"{tnx_chg:+.2f}%")
        
        if tnx_val >= 4.5: adv = "🚨 **[금리 발작: 비상]** 국채 금리가 4.5%를 넘어섰네! 기술주 성벽 무너질 수 있으니 진격을 멈추시게."
        elif n_chg > 0.5 and tnx_chg < 0: adv = "🔥 **[골디락스 진입]** 지수는 오르고 금리는 내리니 기세 타시게."
        else: adv = "🧐 **[눈치싸움 중]** 세력들이 간 보고 있구먼. 섣부른 판단은 독이네."
        st.info(f"🧐 이수 할배의 글로벌 판독: {adv}")
    except: st.error("⚠️ 글로벌 데이터 호출 불가")

st.title("🧐 이수할아버지의 주식 진단기 v36056")
display_global_risk(); st.divider()

symbol = st.text_input("📊 분석할 종목번호 또는 티커 입력", "005930")

if symbol:
    try:
        is_kr = symbol.isdigit()
        start_date = datetime.now() - timedelta(days=500)
        
        if is_kr:
            df = fdr.DataReader(symbol, start=start_date.strftime('%Y-%m-%d'))
            ticker = yf.Ticker(f"{symbol}.KS")
            try:
                df_krx = fdr.StockListing('KRX')
                name = df_krx[df_krx['Code'] == symbol]['Name'].values[0]
            except: name = symbol
            currency, fmt_p = "원", ",.0f"
            # 네이버 실시간 낚시
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            p = float(soup.select_one(".no_today .blind").text.replace(",", ""))
            v_curr = float(soup.select(".no_info .blind")[3].text.replace(",", ""))
            prev_p = float(df['Close'].iloc[-1])
        else:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date)
            name = ticker.info.get('shortName', symbol)
            currency, fmt_p = "$", ",.2f"
            p = float(df['Close'].iloc[-1])
            v_curr = float(df['Volume'].iloc[-1])
            prev_p = float(df['Close'].iloc[-2])

        if not df.empty:
            df = df.ffill().dropna()
            p_diff, p_chg = p - prev_p, (p - prev_p) / prev_p * 100

            # 시간 보정 화력 계산
            tz = pytz.timezone('Asia/Seoul') if is_kr else pytz.timezone('US/Eastern')
            now_local = datetime.now(tz)
            s_h, s_m = (9, 0) if is_kr else (9, 30)
            m_start = now_local.replace(hour=s_h, minute=s_m, second=0, microsecond=0)
            
            v_avg5 = float(df['Volume'].iloc[-6:-1].mean())
            v_ratio = (v_curr / v_avg5) * 100 if v_avg5 > 0 else 0
            
            if now_local < m_start: vol_strength = v_ratio
            else:
                elapsed = (now_local - m_start).seconds / 60
                if now_local.weekday() >= 5 or elapsed > 390: elapsed = 390
                elif elapsed < 10: elapsed = 10 
                vol_strength = v_ratio / (elapsed / 390)
            
            if vol_strength > 1000: vol_strength = v_ratio

            # --- [지표 정밀 계산] ---
            df['RSI'] = ta.rsi(df['Close'], length=14)
            rsi_val, rsi_prev = df['RSI'].iloc[-1], df['RSI'].iloc[-2]
            
            df['Will'] = ta.willr(df['High'], df['Low'], df['Close'], length=14)
            will_val = df['Will'].iloc[-1]
            
            macd_df = ta.macd(df['Close'], fast=12, slow=26, signal=9)
            m_l, s_l = macd_df.iloc[-1, 0], macd_df.iloc[-1, 2]
            m_p, s_p = macd_df.iloc[-2, 0], macd_df.iloc[-2, 2]
            
            bb = ta.bbands(df['Close'], length=20, std=2)
            mid_line = bb.iloc[-1, 0]; low_b = bb.iloc[-1, 1]; up_b = bb.iloc[-1, 2]
            
            peak_20 = float(df['High'].iloc[-21:-1].max())
            defense_line = peak_20 * 0.93

            # --- [화면 출력: 현재가 및 화력] ---
            st.markdown("### 📊 현재주가현황")
            display_price = f"{p:{fmt_p}}{currency} (전일비: {p_diff:+{fmt_p}} / {p_chg:+.2f}%)"
            st.markdown(f"""<div style='background-color:#f8f9fa; padding:20px; border-radius:10px; border-left:10px solid #1565C0;'>
                <p style='font-size:35px; color:#1565C0; font-weight:bold; margin:0;'>{name} ({symbol})</p>
                <p style='font-size:30px; color:#FF4B4B; font-weight:bold; margin:10px 0 0 0;'>{display_price}</p></div>""", unsafe_allow_html=True)

            if vol_strength >= 150: v_status, v_adv = "과열폭발", f"🔥 **[화력폭발]** 현재 강도 {vol_strength:.1f}점! 본진 진격 중이오."
            elif vol_strength >= 100: v_status, v_adv = "매집시작", f"🚀 **[매집시작]** 현재 강도 {vol_strength:.1f}점! 화력이 차오르니 눈여겨보시게."
            elif vol_strength >= 80: v_status, v_adv = "정상화력", f"⚔️ **[정상화력]** 현재 강도 {vol_strength:.1f}점! 기세가 빳빳하구먼."
            else: v_status, v_adv = "거래절벽", f"🧊 **[거래절벽]** 현재 강도 {vol_strength:.1f}점! 속지 마시게."

            st.markdown(f"""<div class='vol-box'><div style='font-size: 32px; font-weight: bold; color: #0D47A1;'>📊 거래량 전황: {v_status} ({v_ratio:.1f}% / 5일평균)</div>
                <div class='vol-sub-text'>{v_adv}</div></div>""", unsafe_allow_html=True)

            # --- [신호등 및 핵심 좌표] ---
            if p >= up_b or rsi_val >= 60: sig, col, s_adv = "🟢 매도권 진입", "#388E3C", "● 과열권일세! 수익 챙기시게."
            elif p <= low_b or rsi_val <= 35: sig, col, s_adv = "🔴 매수권 진입", "#D32F2F", "● 바닥권일세. 겁먹지 말고 보따리 푸시게."
            else: sig, col, s_adv = "🟡 관망 및 대기", "#FBC02D", "● 눈치싸움 중일세. 지표 끝단을 기다리시게."
            
            st.markdown(f"<div class='signal-box' style='background-color:{col};'><p class='signal-text'>{sig}</p><p style='color:white; font-size:20px;'>{s_adv}</p></div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='price-card'><p>⚖️ 공략 대기선</p><p style='color:#388E3C; font-size:32px;'>{format(low_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='price-card'><p>🎯 수확 목표선</p><p style='color:#D32F2F; font-size:32px;'>{format(up_b, fmt_p)}</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='price-card'><p>🛡️ 성벽(방어선)</p><p style='color:#E65100; font-size:32px;'>{format(defense_line, fmt_p)}</p></div>", unsafe_allow_html=True)

            # --- [필살 대응 전략 상세 판독] ---
            adv1 = f"1. **RSI({rsi_val:.1f}):** {'👺 불지옥 문턱일세! 탐욕을 버려야 살 길이오.' if rsi_val >= 60 else '🧊 냉골 바닥이구먼. 이제 보따리 챙길 때가 왔소.' if rsi_val <= 35 else '안개 속 눈치싸움 중이니 섣부른 진격은 금물이오.'}"
            adv2 = f"2. **성벽({format(defense_line, fmt_p)}):** {'🚨 성벽이 무너졌소! 지하실 입구니 절대 속지 마시게.' if p < defense_line else '🏰 성벽 사수 중! 아군 진격의 든든한 발판이오.'}"
            adv3 = f"3. **엔진(MACD):** {'⚙️ 엔진 정회전! 기세가 빳빳하게 붙었구먼.' if m_l > s_l else '🛑 엔진 역회전! 거꾸로 도는 차에 타면 전멸이오.'}"
            
            if m_l < s_l: final_adv = f"🧐 **[최종 결론]** 강도({vol_strength:.1f}점). 엔진 역회전 상태! **무조건 관망하시게!**"
            elif p < defense_line: final_adv = f"⚠️ **[최종 결론]** 강도({vol_strength:.1f}점). 성벽 함락! **현금 확보 및 대기!**"
            elif p >= up_b: final_adv = f"💰 **[최종 결론]** 강도({vol_strength:.1f}점). 목표선 도달! **야금야금 분할 매수 시작!**"
            else: final_adv = f"📈 **[최종 결론]** 강도({vol_strength:.1f}점). 추세 유지 중! **보유(홀딩)하시게.**"

            st.markdown(f"""<div class='trend-card'><div class='trend-title'>⚔️ {name} 실전 필살 대응 전략</div>
                <div class='trend-item'>{adv1}</div><div class='trend-item'>{adv2}</div><div class='trend-item'>{adv3}</div>
                <hr style='border:1px solid #FFEBEE;'><div class='trend-item' style='color:#D32F2F; font-size:25px;'>{final_adv}</div></div>""", unsafe_allow_html=True)

            # --- [4대 지수 정밀 진단 상세 복원] ---
            st.divider(); i1, i2, i3, i4 = st.columns(4)
            with i1: # Bollinger
                bb_diag = "👺 **[천장 돌파]** 울타리 밖으로 기세 폭발! 탐욕의 끝이니 익절하시게." if p >= up_b else \
                          "🧊 **[바닥 돌파]** 지하실 진입! 겁먹지 말고 엔진 시동을 기다리시게." if p <= low_b else \
                          "⚠️ **[과열 진입]** 중앙선 위 안착! 온도가 높으니 수익 챙길 준비!" if p >= mid_line else \
                          "🏠 **[기세 둔화]** 중앙선 밑일세. 온도가 낮아도 절대 칼 뽑지 마시게."
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Bollinger (기세)</p><p class='ind-diag'>{bb_diag}</p></div>", unsafe_allow_html=True)
            
            with i2: # RSI
                is_div = (p > prev_p and rsi_val < rsi_prev)
                r_diag = f"● 지수 {rsi_val:.2f}: {'👺 불지옥 문턱!' if rsi_val >= 60 else '🧊 냉골 바닥!' if rsi_val <= 35 else '⚖️ 중립 구간일세. 지표 끝단을 빳빳하게 기다리시게.'} "
                         f"{'🚨 [배신 포착] 주가는 오르나 온도는 식네! 가짜 상승 주의!' if is_div else ''}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>RSI (온도)</p><p style='font-size:40px; color:#E65100;'>{rsi_val:.2f}</p><p class='ind-diag'>{r_diag}</p></div>", unsafe_allow_html=True)
            
            with i3: # Williams %R
                w_diag = f"● 지수 {will_val:.2f}: {'🚀 천장 광기! 비수 꽂히기 전 수확하시게.' if will_val >= -20 else '📉 하락 가속! 바닥 확인 전 자중하시게.' if will_val <= -80 else '🌫️ 안갯속 구간이네. 기세가 꺾이는지 눈 부라리고 보시게.'}"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>Williams %R</p><p style='font-size:40px; color:#E65100;'>{will_val:.2f}</p><p class='ind-diag'>{w_diag}</p></div>", unsafe_allow_html=True)
            
            with i4: # MACD
                m_diff, m_diff_p = m_l - s_l, m_p - s_p
                m_diag = "⚙️ 엔진 **정회전**! 기세 좋으니 성벽 보며 진격!" if m_l > s_l else \
                         "🛑 엔진 **역회전폭 급감**! 시동 걸 채비 중이니 대기!" if m_diff > m_diff_p else \
                         "🚨 엔진 **역회전 심화**! 거꾸로 도는 차에 타면 전멸!"
                st.markdown(f"<div class='ind-box'><p class='ind-title'>MACD (엔진)</p><p class='ind-diag'>{m_diag}</p></div>", unsafe_allow_html=True)

    except Exception as e: st.error(f"👵 아이구! 오류가 났네: {e}")
