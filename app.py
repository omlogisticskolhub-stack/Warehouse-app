from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Page Configuration - Clean & Fast Dashboard
st.set_page_config(
    page_title="Floor Ops Analytics - Om Logistics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 🔒 SECURITY
# ==========================================
DASHBOARD_PASSWORD = st.secrets.get("DASHBOARD_PASSWORD", "Dhiraj@01072026")


def check_password():
    if "password_correct" not in st.session_state:

        def password_entered():
            if st.session_state["entered_password"] == DASHBOARD_PASSWORD:
                st.session_state["password_correct"] = True
                del st.session_state["entered_password"]
            else:
                st.session_state["password_correct"] = False

        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🚛 Floor Ops Analytics - Om Logistics")
            st.text_input(
                "🔒 Enter Password to Access:",
                type="password",
                on_change=password_entered,
                key="entered_password",
            )
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🚛 Floor Ops Analytics - Om Logistics")
            st.text_input(
                "🔒 Enter Password to Access:",
                type="password",
                key="entered_password",
            )
            st.error("❌ Incorrect Password!")
        return False
    return True


if not check_password():
    st.stop()

# ==========================================
# 🎨 HIGH GRAPHICS THEME CONTROLLER
# ==========================================
with st.sidebar:
    st.markdown("## 🎨 Visual Controls")
    theme_choice = st.selectbox(
        "Choose Dashboard Theme:",
        options=[
            "Om Red (Default)",
            "Dark Neon Glass",
            "Modern Corporate Blue",
            "Emerald Ops",
        ],
        index=0,
    )
    st.markdown("---")
    if st.button("🔒 Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

# Theme CSS Injector
THEMES = {
    "Om Red (Default)": {
        "bg": "#f8fafc",
        "card_bg": "#ffffff",
        "primary": "#d32f2f",
        "text": "#0f172a",
        "card_border": "#e2e8f0",
        "plotly_template": "plotly_white",
    },
    "Dark Neon Glass": {
        "bg": "#0f172a",
        "card_bg": "#1e293b",
        "primary": "#38bdf8",
        "text": "#f8fafc",
        "card_border": "#334155",
        "plotly_template": "plotly_dark",
    },
    "Modern Corporate Blue": {
        "bg": "#f1f5f9",
        "card_bg": "#ffffff",
        "primary": "#2563eb",
        "text": "#1e293b",
        "card_border": "#cbd5e1",
        "plotly_template": "plotly_white",
    },
    "Emerald Ops": {
        "bg": "#f0fdf4",
        "card_bg": "#ffffff",
        "primary": "#16a34a",
        "text": "#064e3b",
        "card_border": "#bbf7d0",
        "plotly_template": "plotly_white",
    },
}

current_theme = THEMES[theme_choice]

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: {current_theme["bg"]} !important;
        color: {current_theme["text"]} !important;
    }}
    
    /* Premium Header */
    .hub-header {{
        background: linear-gradient(135deg, {current_theme["primary"]} 0%, #000000 100%);
        padding: 20px 30px;
        margin: -4rem -2rem 24px -2rem;
        border-bottom: 4px solid {current_theme["primary"]};
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
        color: #ffffff !important;
    }}
    .hub-title {{
        font-size: 28px !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        color: #ffffff !important;
    }}
    .hub-subtitle {{
        font-size: 14px;
        opacity: 0.9;
        color: #f1f5f9 !important;
    }}

    /* High Graphics KPI Cards */
    div[data-testid="stMetric"] {{
        background: {current_theme["card_bg"]} !important;
        padding: 16px !important;
        border-radius: 12px !important;
        border: 1px solid {current_theme["card_border"]} !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 26px !important;
        color: {current_theme["text"]} !important;
        font-weight: 800 !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 11px !important;
        color: {current_theme["text"]} !important;
        opacity: 0.7;
        font-weight: 700 !important;
        text-transform: uppercase;
    }}

    /* Filter Box Styling */
    .filter-card {{
        background-color: {current_theme["card_bg"]};
        padding: 15px;
        border-radius: 12px;
        border: 1px solid {current_theme["card_border"]};
        margin-bottom: 20px;
    }}

    /* Section Headings */
    .section-head {{
        font-size: 17px;
        font-weight: 800;
        color: {current_theme["text"]};
        padding-bottom: 6px;
        margin-bottom: 12px;
        border-bottom: 2px solid {current_theme["primary"]};
    }}

    /* Hide Streamlit Artifacts */
    #MainMenu, header, footer, [data-testid="stHeader"] {{ visibility: hidden !important; display: none !important; }}
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hub-header">
        <div class="hub-title">🚛 FLOOR OPS | AGING & PENDENCY ANALYTICS</div>
        <div class="hub-subtitle">Kolkata Regional Hubs - High-Graphics Real-Time Performance Dashboard</div>
    </div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# ⚡ CACHED DATA PROCESSING (SUPER FAST)
# ==========================================
@st.cache_data(show_spinner=False)
def process_data(file_bytes):
    df_raw = pd.read_excel(file_bytes)
    df_raw.columns = df_raw.columns.str.strip().str.upper()

    def find_col(keys):
        for k in keys:
            for c in df_raw.columns:
                if k in c:
                    return c
        return None

    col_cn = find_col(["CN_CN_NO", "CN_NO", "WAYBILL", "LR_NO"])
    col_pkg = find_col(["CN_PKG", "PKG", "QTY"])
    col_wt = find_col(["ACT_WT", "WT", "WEIGHT", "CN_ACTUAL_WEIGHT"])
    col_todist = find_col(["TODIST", "DESTINATION", "HUB"])
    col_gatein_date = find_col(["CHLN_GATE_IN_DATE", "GATE_IN_DATE"])
    col_cn_date = find_col(["CN_DATE", "BOOKING_DATE"])
    col_days = find_col(["CN_TOTAL_DAYS", "AGEING", "DAYS"])
    col_reason = find_col(["UNDLVRD_REASON", "REASON", "REMARKS"])
    col_mode = find_col(["MODE", "TRANSIT"])
    col_cee = find_col(["CEE", "CONSIGNEE", "CLIENT"])
    col_pin = find_col(["CEE_PINCODE", "PINCODE", "PIN"])

    df = df_raw.drop_duplicates(subset=[col_cn]).copy() if col_cn else df_raw

    today = pd.to_datetime(datetime.today().date())
    p_date = (
        pd.to_datetime(df[col_gatein_date], dayfirst=True, errors="coerce")
        if col_gatein_date
        else pd.Series(dtype="datetime64[ns]")
    )
    f_date = (
        pd.to_datetime(df[col_cn_date], dayfirst=True, errors="coerce")
        if col_cn_date
        else pd.Series(dtype="datetime64[ns]")
    )

    df["DATE_OBJ"] = p_date.fillna(f_date)
    df["GATE_IN_DAY"] = (
        df["DATE_OBJ"].dt.strftime("%d-%b-%Y").fillna("Date Missing")
    )

    if col_days:
        df["CALCULATED_DAYS"] = (
            pd.to_numeric(df[col_days], errors="coerce")
            .fillna((today - df["DATE_OBJ"]).dt.days.fillna(0))
            .astype(int)
        )
    else:
        df["CALCULATED_DAYS"] = (
            (today - df["DATE_OBJ"])
            .dt.days.fillna(0)
            .apply(lambda x: max(0, int(x)))
        )

    df["CALCULATED_HOURS"] = df["CALCULATED_DAYS"] * 24

    def assign_bucket(hrs):
        if hrs >= 96:
            return "96 Hour Above"
        if hrs >= 72:
            return "72 Hour Above"
        if hrs >= 48:
            return "48 Hour Above"
        if hrs >= 24:
            return "24 Hour Above"
        return "24 Hour Below"

    df["Aging_Bucket"] = df["CALCULATED_HOURS"].apply(assign_bucket)
    df["CN_PKG_NUM"] = (
        pd.to_numeric(df[col_pkg], errors="coerce").fillna(0).astype(int)
        if col_pkg
        else 0
    )
    df["CN_WT_NUM"] = (
        pd.to_numeric(df[col_wt], errors="coerce").fillna(0).round(1)
        if col_wt
        else 0.0
    )

    if col_reason:
        df["REASON_CLEAN"] = df[col_reason].apply(
            lambda x: "Pending Reason"
            if pd.isnull(x) or str(x).strip() in ["", "-", "NAN", "NONE"]
            else str(x).strip()
        )
        df["REASON_STATUS"] = df["REASON_CLEAN"].apply(
            lambda x: "Missing" if x == "Pending Reason" else "Filled"
        )

    cols = {
        "cn": col_cn,
        "pkg": col_pkg,
        "wt": col_wt,
        "todist": col_todist,
        "gatein": col_gatein_date,
        "cndate": col_cn_date,
        "reason": col_reason,
        "mode": col_mode,
        "cee": col_cee,
        "pin": col_pin,
    }
    return df, cols


uploaded_file = st.file_uploader(
    "Upload Operations Excel Sheet (.xlsx, .xls)", type=["xlsx", "xls"]
)

if uploaded_file is not None:
    df_raw_loaded, cols = process_data(uploaded_file)
    col_cn, col_pkg, col_wt, col_todist = (
        cols["cn"],
        cols["pkg"],
        cols["wt"],
        cols["todist"],
    )
    col_gatein_date, col_cn_date, col_reason = (
        cols["gatein"],
        cols["cndate"],
        cols["reason"],
    )
    col_mode, col_cee = cols["mode"], cols["cee"]

    # Unique Option Lists
    all_hubs = (
        sorted(df_raw_loaded[col_todist].dropna().astype(str).unique().tolist())
        if col_todist
        else []
    )
    all_dates = (
        df_raw_loaded.dropna(subset=["DATE_OBJ"])
        .sort_values(by="DATE_OBJ", ascending=False)["GATE_IN_DAY"]
        .unique()
        .tolist()
    )
    all_cees = (
        sorted(df_raw_loaded[col_cee].dropna().astype(str).unique().tolist())
        if col_cee
        else []
    )
    all_reasons = (
        sorted(
            df_raw_loaded[df_raw_loaded["REASON_STATUS"] == "Filled"][
                "REASON_CLEAN"
            ]
            .unique()
            .tolist()
        )
        if col_reason
        else []
    )

    kpi_placeholder = st.empty()

    # =========================================================
    # 🔘 MASTER FILTERS WITH TICK-BOX (TOGGLE ALL)
    # =========================================================
    st.markdown("### 🔍 Filters & Selection Controls")
    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)

    with f_col1:
        chk_hub = st.checkbox("☑️ Select All Hubs", value=False)
        selected_hubs = st.multiselect(
            "🏢 TODIST Hub:",
            options=all_hubs,
            default=all_hubs if chk_hub else [],
        )

    with f_col2:
        chk_date = st.checkbox("☑️ Select All Dates", value=True)
        selected_dates = st.multiselect(
            "🗓️ Gate-In Date:",
            options=all_dates,
            default=all_dates if chk_date else [],
        )

    with f_col3:
        chk_cee = st.checkbox("☑️ Select All CEEs", value=False)
        selected_cees = st.multiselect(
            "👤 CEE / Consignee:",
            options=all_cees,
            default=all_cees if chk_cee else [],
        )

    with f_col4:
        reason_status_filter = st.selectbox(
            "⚡ Reason Status:",
            ["All Status", "Pending Reason Only", "Updated Reason Only"],
        )

    with f_col5:
        chk_reason = st.checkbox("☑️ Select All Reasons", value=False)
        selected_reasons = st.multiselect(
            "⚠️ Specific Reason:",
            options=all_reasons,
            default=all_reasons if chk_reason else [],
        )

    # Filtering Data
    df_filtered = df_raw_loaded.copy()

    if selected_hubs:
        df_filtered = df_filtered[
            df_filtered[col_todist].astype(str).isin(selected_hubs)
        ]
    if selected_dates:
        df_filtered = df_filtered[
            df_filtered["GATE_IN_DAY"].isin(selected_dates)
        ]
    else:
        df_filtered = df_filtered.iloc[0:0]

    if selected_cees and col_cee:
        df_filtered = df_filtered[
            df_filtered[col_cee].astype(str).isin(selected_cees)
        ]

    if reason_status_filter == "Pending Reason Only":
        df_filtered = df_filtered[df_filtered["REASON_STATUS"] == "Missing"]
    elif reason_status_filter == "Updated Reason Only":
        df_filtered = df_filtered[df_filtered["REASON_STATUS"] == "Filled"]

    if selected_reasons:
        df_filtered = df_filtered[
            df_filtered["REASON_CLEAN"].isin(selected_reasons)
        ]

    df = df_filtered.copy()

    # Dynamic Weight Formatting
    def format_weight(kg):
        return f"{kg / 1000:.2f} Ton" if kg >= 1000 else f"{kg:.1f} KG"

    # KPI Calculation
    tot_cn = len(df)
    tot_pkg = df["CN_PKG_NUM"].sum() if tot_cn > 0 else 0
    tot_wt = df["CN_WT_NUM"].sum() if tot_cn > 0 else 0
    avg_days = round(df["CALCULATED_DAYS"].mean(), 1) if tot_cn > 0 else 0
    pending_reasons = (
        len(df[df["REASON_STATUS"] == "Missing"]) if col_reason else 0
    )

    with kpi_placeholder.container():
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Unique CNs", f"{tot_cn:,}")
        c2.metric("Total Packages", f"{tot_pkg:,}")
        c3.metric("Weight Load", format_weight(tot_wt))
        c4.metric(
            "🚨 >96 Hours", f"{len(df[df['Aging_Bucket']=='96 Hour Above']):,}"
        )
        c5.metric("Avg Aging", f"{avg_days} Days")
        c6.metric("Blank Reason CNs", f"{pending_reasons:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================================================
    # HIGH-GRAPHICS VISUALIZATIONS (PLOTLY)
    # =========================================================
    g1, g2 = st.columns(2)

    with g1:
        st.markdown(
            "<div class='section-head'>📊 Aging Hours Breakdown</div>",
            unsafe_allow_html=True,
        )
        bucket_order = [
            "96 Hour Above",
            "72 Hour Above",
            "48 Hour Above",
            "24 Hour Above",
            "24 Hour Below",
        ]
        b_df = (
            df["Aging_Bucket"]
            .value_counts()
            .reindex(bucket_order)
            .fillna(0)
            .reset_index()
        )
        b_df.columns = ["Bucket", "Count"]

        fig_b = px.bar(
            b_df,
            x="Bucket",
            y="Count",
            text="Count",
            color="Bucket",
            color_discrete_map={
                "96 Hour Above": "#ef4444",
                "72 Hour Above": "#f97316",
                "48 Hour Above": "#eab308",
                "24 Hour Above": "#3b82f6",
                "24 Hour Below": "#22c55e",
            },
            template=current_theme["plotly_template"],
        )
        fig_b.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_b, use_container_width=True)

    with g2:
        st.markdown(
            "<div class='section-head'>⚠️ Top Delay Reasons</div>",
            unsafe_allow_html=True,
        )
        if col_reason:
            r_df = (
                df[df["REASON_STATUS"] == "Filled"]["REASON_CLEAN"]
                .value_counts()
                .head(6)
                .reset_index()
            )
            r_df.columns = ["Reason", "Count"]

            if len(r_df) > 0:
                fig_r = px.bar(
                    r_df,
                    x="Count",
                    y="Reason",
                    orientation="h",
                    text="Count",
                    color="Count",
                    color_continuous_scale="Reds",
                    template=current_theme["plotly_template"],
                )
                fig_r.update_layout(
                    height=320,
                    margin=dict(l=10, r=10, t=10, b=10),
                    yaxis={"categoryorder": "total ascending"},
                )
                st.plotly_chart(fig_r, use_container_width=True)
            else:
                st.info("No delay reasons updated for current filters.")

    # Operations Data Table
    st.markdown(
        "<div class='section-head'>📋 Clean Operations Data</div>",
        unsafe_allow_html=True,
    )
    disp_cols = [
        c for c in [col_cn, col_todist, col_cee, col_pkg, col_wt, col_reason] if c
    ]
    st.dataframe(
        df[disp_cols + ["CALCULATED_DAYS", "Aging_Bucket"]],
        use_container_width=True,
        height=300,
    )
