from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Page Configuration - Clean Dashboard
st.set_page_config(page_title="Floor Ops Dashboard - Om Logistics", layout="wide")

# ==========================================
# 🎨 DASHBOARD STYLING
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        color: #000000 !important;
    }

    .stApp {
        background-color: #f4f6f9;
    }

    .hub-header {
        background-color: #ffffff;
        padding: 16px 28px;
        margin: -4rem -2rem 20px -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 3px solid #d32f2f;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .hub-title {
        font-size: 26px !important;
        font-weight: 900 !important;
        color: #d32f2f !important;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hub-subtitle {
        font-size: 14px;
        color: #111827;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background: #ffffff !important;
        padding: 14px 16px !important;
        border-radius: 8px !important;
        border: 2px solid #cbd5e1 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        text-align: left;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        color: #000000 !important;
        font-weight: 900 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px !important;
        color: #000000 !important;
        text-transform: uppercase;
        font-weight: 800 !important;
        letter-spacing: 0.5px;
    }

    .section-head {
        font-size: 18px;
        font-weight: 900;
        color: #000000;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 3px solid #d32f2f;
    }

    div[data-testid="stTable"], div[data-testid="stDataFrame"] {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stFileUploader"] {
        background-color: #ffffff;
        border: 2px dashed #94a3b8;
        border-radius: 8px;
        padding: 10px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        padding-top: 0px;
        padding-bottom: 0px;
        font-weight: 800 !important;
    }

    #MainMenu { visibility: hidden !important; display: none !important; }
    header { visibility: hidden !important; display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    footer * { visibility: hidden !important; display: none !important; }
    [data-testid="stHeader"] { visibility: hidden !important; display: none !important; }
    [data-testid="stAppToolbar"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    .viewerBadge_container__1S-5D, .viewerBadge_link__1S-5D { display: none !important; }
    #stDecoration { display: none !important; }
    div[class*="viewerBadge"] { display: none !important; }
    div[class*="styles_viewerBadge"] { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    button[title="View fullscreen"] { display: none !important; }
    a[href*="streamlit.io"] { display: none !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hub-header">
        <div>
            <div class="hub-title"><span>🚛</span> FLOOR OPS | AGING & PENDENCY ANALYTICS</div>
            <div class="hub-subtitle">Kolkata Regional Hubs - Gate-In & Delivery Delay Tracking</div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)


def format_weight(kg_val):
    if kg_val >= 1000:
        return f"{kg_val / 1000:.2f} Ton"
    else:
        return f"{kg_val:.1f} KG"


if "processed_df" not in st.session_state:
    st.session_state["processed_df"] = None

# ==========================================
# STEP 1: FILE UPLOADER
# ==========================================
uploaded_file = st.file_uploader(
    "Upload Operations Excel Sheet (.xlsx, .xls)", type=["xlsx", "xls"]
)

if uploaded_file is not None:
    with st.spinner("Processing Operations Data & Removing Duplicates..."):
        df_raw = pd.read_excel(uploaded_file)
        df_raw.columns = df_raw.columns.str.strip().str.upper()

        def find_column(possible_names, df):
            for name in possible_names:
                for col in df.columns:
                    if name in col:
                        return col
            return None

        col_cn = find_column(
            ["CN_CN_NO", "CN_NO", "WAYBILL", "LR_NO", "CN"], df_raw
        )
        col_pkg = find_column(
            ["CN_PKG", "PKG", "BOX", "QTY", "PIECES"], df_raw
        )
        col_wt = find_column(
            ["ACT_WT", "CHG_WT", "WT", "WEIGHT", "TOTAL_WEIGHT", "KGS"], df_raw
        )
        col_todist = find_column(
            ["TODIST", "DESTINATION", "LOCATION", "HUB"], df_raw
        )
        col_gatein_date = find_column(
            ["CHLN_GATE_IN_DATE", "GATE_IN_DATE", "GATE_IN", "GATEIN"], df_raw
        )
        col_cn_date = find_column(["CN_DATE", "BOOKING_DATE"], df_raw)
        col_days = find_column(
            ["CN_TOTAL_DAYS", "AGEING", "DAYS", "PENDING_DAYS"], df_raw
        )
        col_reason = find_column(
            ["UNDLVRD_REASON", "REASON", "REMARKS", "DELAY_REASON"], df_raw
        )
        col_mode = find_column(
            ["MODE", "SERVICE", "PRIORITY", "TRANSIT"], df_raw
        )
        col_cee = find_column(
            ["CEE", "CONSIGNEE", "CLIENT", "RECEIVER"], df_raw
        )
        col_pin = find_column(
            ["CEE_PINCODE", "PINCODE", "PIN_CODE", "PIN", "DEST_PIN"], df_raw
        )

        df = df_raw.copy()

        # Deduplicate based on CN
        if col_cn:
            df = df.drop_duplicates(subset=[col_cn]).copy()

        today = pd.to_datetime(datetime.today().date())

        # Gate-In Date / Fallback CN Date Logic
        primary_date = (
            pd.to_datetime(df[col_gatein_date], dayfirst=True, errors="coerce")
            if col_gatein_date
            else pd.Series(dtype="datetime64[ns]")
        )
        fallback_date = (
            pd.to_datetime(df[col_cn_date], dayfirst=True, errors="coerce")
            if col_cn_date
            else pd.Series(dtype="datetime64[ns]")
        )

        df["DATE_OBJ"] = primary_date.fillna(fallback_date)
