import streamlit as st
from datetime import datetime
import io

# --- PDF LIBRARY IMPORT ---
try:
    from fpdf import FPDF
except ImportError:
    st.error("⚠️ PDF Library 'fpdf' not found. Please add 'fpdf' to your requirements.txt on GitHub.")

# ---------------- 1. INITIALIZE GLOBAL STATE ---------------- #
if "balance" not in st.session_state:
    st.session_state.balance = 2146.11  
if "trades_taken" not in st.session_state:
    st.session_state.trades_taken = 0
if "trade_notes" not in st.session_state:
    st.session_state.trade_notes = ""

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- PDF REPORT GENERATOR CLASS ---------------- #
class TradeReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, 'BLACKARROWFX PRECISION REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Timestamp: {dt_string}', 0, 1, 'C')
        self.ln(10)

    def section_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, label, 0, 1, 'L', 1)
        self.ln(4)

def create_pdf(data):
    pdf = TradeReport()
    pdf.add_page()
    
    # 1. Overview
    pdf.section_title('1. INSTRUMENT & RISK OVERVIEW')
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f"Symbol: {data['symbol']} | Direction: {data['direction']}", 0, 1)
    pdf.cell(0, 7, f"Entry: {data['entry']} | SL: {data['sl']} | TP1: {data['tp1']}", 0, 1)
    pdf.ln(5)

    # 2. Timeframes Table
    pdf.section_title('2. QUAD TIMEFRAME SWING DATA')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(30, 8, 'TF', 1, 0, 'C')
    pdf.cell(40, 8, 'Bias', 1, 0, 'C')
    pdf.cell(60, 8, 'Swing High', 1, 0, 'C')
    pdf.cell(60, 8, 'Swing Low', 1, 0, 'C')
    pdf.ln()
    
    pdf.set_font('Arial', '', 10)
    tfs = [
        ("4H", data['4h_b'], data['s4h'], data['s4l']),
        ("1H", data['1h_b'], data['s1h'], data['s1l']),
        ("30M", data['30m_b'], data['s30h'], data['s30l']),
        ("15M", data['15m_b'], data['s15h'], data['s15l'])
    ]
    for tf, bias, hi, lo in tfs:
        pdf.cell(30, 8, tf, 1, 0, 'C')
        pdf.cell(40, 8, bias, 1, 0, 'C')
        pdf.cell(60, 8, str(hi), 1, 0, 'C')
        pdf.cell(60, 8, str(lo), 1, 0, 'C')
        pdf.ln()
    pdf.ln(5)

    # 3. Strategy Notes
    pdf.section_title('3. POST-SHOCK EXECUTION PLAN')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, data['notes'])
    
    return pdf.output(dest='S').encode('latin-1')

# ---------------- SIDEBAR: RISK & SYSTEM ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    asset_type = st.selectbox("Select Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"])
    symbol = st.text_input("Enter Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")
    st.session_state.balance = st.number_input("Current Balance ($)", value=float(st.session_state.balance), format="%.2f")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0)

    st.markdown("---")
    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News Active", value=False) 

# ---------------- MAIN INTERFACE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.markdown("---")

# ---------------- QUAD TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)
with c4h:
    st.subheader("⏳ 4H BIAS")
    htf_bias = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t")
    s4_h = st.number_input("Swing High", value=0.0, format="%.2f", key="s4h")
    s4_l = st.number_input("Swing Low", value=0.0, format="%.2f", key="s4l")
    bias_4h_ok = st.checkbox("4H Confirmed", key="4h_c")

with c1h:
    st.subheader("⏱️ 1H STRUC")
    itf_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t")
    s1_h = st.number_input("1H High", value=0.0, format="%.2f", key="s1h")
    s1_l = st.number_input("1H Low", value=0.0, format="%.2f", key="s1l")
    bias_1h_ok = st.checkbox("1H Confirmed", key="1h_c")

with c30m:
    st.subheader("⚡ 30M SHIFT")
    t30_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="30m_t")
    s30_h = st.number_input("30M High", value=0.0, format="%.2f", key="s30h")
    s30_l = st.number_input("30M Low", value=0.0, format="%.2f", key="s30l")
    bias_30m_ok = st.checkbox("30M Confirmed", key="30m_c")

with c15m:
    st.subheader("🎯 15M ENTRY")
    t15_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="15m_t")
    s15_h = st.number_input("15M High", value=0.0, format="%.2f", key="s15h")
    s15_l = st.number_input("15M Low", value=0.0, format="%.2f", key="s15l")
    bias_15m_ok = st.checkbox("15M Confirmed", key="15m_c")

# ---------------- STRATEGY NOTES ---------------- #
st.markdown("---")
st.subheader("📝 POST-SHOCK EXECUTION PLAN")
st.session_state.trade_notes = st.text_area("Strategic Setup:", value=st.session_state.trade_notes, height=400)

# ---------------- EXECUTION ---------------- #
st.markdown("---")
col_e, col_r = st.columns(2)

with col_e:
    st.header("🚀 PHASE 3: EXECUTE")
    trade_dir = st.radio("Direction", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True)
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f")
    sl_val = st.number_input("Stop Loss", value=0.0, format="%.2f")
    
    pip_f = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    tp1_val = 0
    if entry_val > 0 and sl_val > 0 and trade_dir != "Select...":
        dist = abs(entry_val - sl_val) / pip_f
        tp1_val = entry_val + (dist * 2 * pip_f) if trade_dir == "LONG 🔵" else entry_val - (dist * 2 * pip_f)
        st.metric("TP 1 (1:2)", f"{round(tp1_val, 2)}")

with col_r:
    st.header("📄 PDF REPORT")
    if st.button("PREPARE REPORT SHEET", use_container_width=True):
        try:
            report_data = {
                "symbol": symbol, "direction": trade_dir, "entry": entry_val, "sl": sl_val, "tp1": round(tp1_val, 2),
                "4h_b": htf_bias, "s4h": s4_h, "s4l": s4_l, "1h_b": itf_trend, "s1h": s1_h, "s1l": s1_l,
                "30m_b": t30_trend, "s30h": s30_h, "s30l": s30_l, "15m_b": t15_trend, "s15h": s15_h, "s15l": s15_l,
                "notes": st.session_state.trade_notes
            }
            pdf_bytes = create_pdf(report_data)
            st.download_button(
                label="📥 DOWNLOAD PDF REPORT",
                data=pdf_bytes,
                file_name=f"BlackArrow_Report_{symbol}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error: {e}")
