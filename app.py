import streamlit as st
from datetime import datetime
import io

# --- PDF LIBRARY CHECK ---
try:
    from fpdf import FPDF
except ImportError:
    st.error("⚠️ PDF Library missing! Please add 'fpdf' to your requirements.txt file on GitHub.")

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

# ---------------- PDF REPORT GENERATOR ---------------- #
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
    
    # Section 1: Overview
    pdf.section_title('1. INSTRUMENT & RISK')
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f"Symbol: {data['symbol']}", 0, 1)
    pdf.cell(0, 7, f"Direction: {data['direction']}", 0, 1)
    pdf.cell(0, 7, f"Entry: {data['entry']} | SL: {data['sl']} | TP1: {data['tp1']}", 0, 1)
    pdf.ln(5)

    # Section 2: Timeframes
    pdf.section_title('2. QUAD TIMEFRAME LEVELS')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(30, 8, 'TF', 1)
    pdf.cell(40, 8, 'Bias', 1)
    pdf.cell(60, 8, 'Swing High', 1)
    pdf.cell(60, 8, 'Swing Low', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 10)
    tfs = [
        ("4H", data['4h_b'], data['s4h'], data['s4l']),
        ("1H", data['1h_b'], data['s1h'], data['s1l']),
        ("30M", data['30m_b'], data['s30h'], data['s30l']),
        ("15M", data['15m_b'], data['s15h'], data['s15l'])
    ]
    for tf, bias, hi, lo in tfs:
        pdf.cell(30, 8, tf, 1)
        pdf.cell(40, 8, bias, 1)
        pdf.cell(60, 8, str(hi), 1)
        pdf.cell(60, 8, str(lo), 1)
        pdf.ln()
    pdf.ln(5)

    # Section 3: Notes
    pdf.section_title('3. POST-SHOCK EXECUTION PLAN')
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 7, data['notes'])
    
    # Output to binary string
    return pdf.output(dest='S').encode('latin-1')

# ---------------- SIDEBAR: RISK ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    asset_type = st.selectbox("Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"])
    symbol = st.text_input("Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")
    st.session_state.balance = st.number_input("Balance ($)", value=float(st.session_state.balance), format="%.2f")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk (%)", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk ($)", min_value=1.0, value=50.0)

# ---------------- MAIN UI ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol}")
st.caption(f"Server Time: {dt_string}")
st.markdown("---")

# ---------------- QUAD TIMEFRAME ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)
with c4h:
    st.subheader("⏳ 4H")
    h4_b = st.radio("Bias", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="h4b")
    s4h = st.number_input("4H High", format="%.2f", key="sh4")
    s4l = st.number_input("4H Low", format="%.2f", key="sl4")
with c1h:
    st.subheader("⏱️ 1H")
    h1_b = st.radio("Bias", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="h1b")
    s1h = st.number_input("1H High", format="%.2f", key="sh1")
    s1l = st.number_input("1H Low", format="%.2f", key="sl1")
with c30m:
    st.subheader("⚡ 30M")
    h30_b = st.radio("Bias", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="h30b")
    s30h = st.number_input("30M High", format="%.2f", key="sh30")
    s30l = st.number_input("30M Low", format="%.2f", key="sl30")
with c15m:
    st.subheader("🎯 15M")
    h15_b = st.radio("Bias", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="h15b")
    s15h = st.number_input("15M High", format="%.2f", key="sh15")
    s15l = st.number_input("15M Low", format="%.2f", key="sl15")

# ---------------- STRATEGY BOX ---------------- #
st.markdown("---")
st.subheader("📝 POST-SHOCK EXECUTION PLAN")
st.session_state.trade_notes = st.text_area("Strategic Notes:", value=st.session_state.trade_notes, height=400)

# ---------------- EXECUTION ---------------- #
st.markdown("---")
col_e, col_r = st.columns(2)

with col_e:
    st.header("🚀 EXECUTE")
    trade_dir = st.radio("Direction", ["LONG 🔵", "SHORT 🔴"], horizontal=True)
    entry_val = st.number_input("Entry Price", value=0.0, format="%.2f")
    sl_val = st.number_input("Stop Loss", value=0.0, format="%.2f")
    
    pip_f = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    tp1_val = 0
    if entry_val > 0 and sl_val > 0:
        pips = abs(entry_val - sl_val) / pip_f
        tp1_val = entry_val + (pips * 2 * pip_f) if trade_dir == "LONG 🔵" else entry_val - (pips * 2 * pip_f)
        st.metric("TP1 (1:2)", f"{round(tp1_val, 2)}")
        st.info(f"🛡️ Management: Set BE/Partial at {round(tp1_val, 2)}")

with col_r:
    st.header("📄 PDF ARCHIVE")
    rep_data = {
        "symbol": symbol, "direction": trade_dir, "entry": entry_val, "sl": sl_val, "tp1": round(tp1_val, 2),
        "4h_b": h4_b, "s4h": s4h, "s4l": s4l, "1h_b": h1_b, "s1h": s1h, "s1l": s1l,
        "30m_b": h30_b, "s30h": s30h, "s30l": s30l, "15m_b": h15_b, "s15h": s15h, "s15l": s15l,
        "notes": st.session_state.trade_notes
    }
    
    if st.button("PREPARE PDF REPORT"):
        try:
            pdf_bytes = create_pdf(rep_data)
            st.download_button(
                label="📥 DOWNLOAD TRADE REPORT",
                data=pdf_bytes,
                file_name=f"BlackArrow_{symbol}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except NameError:
            st.error("Cannot generate PDF. Library 'fpdf' not installed.")
