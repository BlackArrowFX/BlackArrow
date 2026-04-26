import streamlit as st
from datetime import datetime
from fpdf import FPDF
import io

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
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'BlackArrowFX Precision Trade Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Generated: {dt_string}', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, label, 0, 1, 'L', 1)
        self.ln(4)

    def trade_table(self, data):
        self.set_font('Arial', 'B', 10)
        # Table Header
        self.cell(30, 7, 'Timeframe', 1)
        self.cell(40, 7, 'Bias', 1)
        self.cell(60, 7, 'Swing High', 1)
        self.cell(60, 7, 'Swing Low', 1)
        self.ln()
        # Table Body
        self.set_font('Arial', '', 10)
        rows = [
            ("4H", data['4h_b'], data['s4h'], data['s4l']),
            ("1H", data['1h_b'], data['s1h'], data['s1l']),
            ("30M", data['30m_b'], data['s30h'], data['s30l']),
            ("15M", data['15m_b'], data['s15h'], data['s15l'])
        ]
        for row in rows:
            self.cell(30, 7, str(row[0]), 1)
            self.cell(40, 7, str(row[1]), 1)
            self.cell(60, 7, str(row[2]), 1)
            self.cell(60, 7, str(row[3]), 1)
            self.ln()

def create_pdf_report(data):
    pdf = TradeReport()
    pdf.add_page()
    
    # 1. Overview
    pdf.chapter_title('1. Instrument Overview')
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f"Symbol: {data['symbol']}", 0, 1)
    pdf.cell(0, 7, f"Direction: {data['direction']}", 0, 1)
    pdf.cell(0, 7, f"Entry: {data['entry']} | SL: {data['sl']} | TP1: {data['tp1']}", 0, 1)
    pdf.ln(5)

    # 2. Quad Timeframe Analysis
    pdf.chapter_title('2. Quad Timeframe Analysis')
    pdf.trade_table(data)
    pdf.ln(5)

    # 3. Strategy Notes
    pdf.chapter_title('3. Post-Shock Execution Plan')
    pdf.set_font('Arial', 'I', 10)
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

# ---------------- MAIN INTERFACE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision")
st.markdown("---")

# ---------------- QUAD TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)
with c4h:
    st.subheader("⏳ 4H BIAS")
    htf_bias = st.radio("4H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t")
    s4_h = st.number_input("4H High", value=0.0, format="%.2f")
    s4_l = st.number_input("4H Low", value=0.0, format="%.2f")
with c1h:
    st.subheader("⏱️ 1H STRUC")
    itf_trend = st.radio("1H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t")
    s1_h = st.number_input("1H High", value=0.0, format="%.2f")
    s1_l = st.number_input("1H Low", value=0.0, format="%.2f")
with c30m:
    st.subheader("⚡ 30M SHIFT")
    t30_trend = st.radio("30M Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="30m_t")
    s30_h = st.number_input("30M High", value=0.0, format="%.2f")
    s30_l = st.number_input("30M Low", value=0.0, format="%.2f")
with c15m:
    st.subheader("🎯 15M ENTRY")
    t15_trend = st.radio("15M Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="15m_t")
    s15_h = st.number_input("15M High", value=0.0, format="%.2f")
    s15_l = st.number_input("15M Low", value=0.0, format="%.2f")

# ---------------- STRATEGY BOX ---------------- #
st.markdown("---")
st.subheader("📝 POST-SHOCK EXECUTION PLAN")
st.session_state.trade_notes = st.text_area("Strategic Setup:", value=st.session_state.trade_notes, height=400)

# ---------------- PHASE 3: EXECUTE ---------------- #
st.markdown("---")
col_e, col_r = st.columns(2)

with col_e:
    st.header("🚀 EXECUTE")
    trade_dir = st.radio("Direction", ["LONG 🔵", "SHORT 🔴"], horizontal=True)
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f")
    sl_val = st.number_input("Stop Loss", value=0.0, format="%.2f")
    
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    tp1 = 0
    if entry_val > 0 and sl_val > 0:
        actual_pips = abs(entry_val - sl_val) / pip_factor
        tp1 = entry_val + (actual_pips * 2 * pip_factor) if trade_dir == "LONG 🔵" else entry_val - (actual_pips * 2 * pip_factor)
        st.write(f"**TP1 (1:2): {round(tp1, 2)}**")

with col_r:
    st.header("📄 PDF REPORT")
    
    report_data = {
        "symbol": symbol, "direction": trade_dir, "entry": entry_val, "sl": sl_val, "tp1": round(tp1, 2),
        "4h_b": htf_bias, "s4h": s4_h, "s4l": s4_l,
        "1h_b": itf_trend, "s1h": s1_h, "s1l": s1_l,
        "30m_b": t30_trend, "s30h": s30_h, "s30l": s30_l,
        "15m_b": t15_trend, "s15h": s15_h, "s15l": s15_l,
        "notes": st.session_state.trade_notes
    }

    if st.button("PREPARE PDF"):
        pdf_output = create_pdf_report(report_data)
        st.download_button(
            label="📥 DOWNLOAD PDF REPORT",
            data=pdf_output,
            file_name=f"BlackArrow_Report_{symbol}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
