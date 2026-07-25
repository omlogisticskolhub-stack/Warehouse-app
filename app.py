import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# Page Configuration - Clean High Contrast Dashboard
st.set_page_config(
    page_title="Floor Ops Dashboard - Om Logistics",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Complete Black & Bold Text Styling CSS + Streamlit UI Hiding
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
    
    /* Hide Streamlit Header, Footer, and Menus */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .viewerBadge_container__1S-5D {display: none !important;}
    
    /* Header Layout */
    .hub-header {
        background: #ffffff;
        padding: 16px 24px;
        border-radius: 8px;
        border-bottom: 3px solid #d32f2f;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .hub-title {
        font-size: 22px;
        font-weight: 900;
        color: #d32f2f;
        letter-spacing: -0.5px;
    }
    .hub-subtitle {
        font-size: 13px;
        font-weight: 700;
        color: #333333;
        margin-top: 2px;
    }
    .hub-meta {
        text-align: right;
        font-size: 13px;
        color: #111111;
        font-weight: 700;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 12px;
        font-weight: 800;
        color: #475569;
        text-transform: uppercase;
    }
    .metric-val {
        font-size: 28px;
        font-weight: 900;
        color: #0f172a;
        margin-top: 4px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Manage Upload State and Timestamp
if "upload_time" not in st.session_state:
    st.session_state["upload_time"] = "Not Uploaded Yet"

# File Uploader Container
uploaded_file = st.file_uploader(
    "📂 Choose / Upload Operations Data Sheet (.xlsx, .xls)",
    type=["xlsx", "xls"],
)

# Update Time dynamically on file upload
if uploaded_file is not None:
    if (
        "last_file_name" not in st.session_state
        or st.session_state.last_file_name != uploaded_file.name
    ):
        st.session_state["upload_time"] = datetime.now().strftime(
            "%d-%b-%Y %I:%M %p"
        )
        st.session_state["last_file_name"] = uploaded_file.name

# Top Navigation Header with Dynamic Time Display
time_color = (
    "#d32f2f"
    if st.session_state["upload_time"] == "Not Uploaded Yet"
    else "#16a34a"
)

st.markdown(
    f"""
    <div class="hub-header">
        <div>
            <div class="hub-title">🚚 FLOOR OPS | AGING & PENDENCY ANALYTICS</div>
            <div class="hub-subtitle">Kolkata Regional Hubs - Gate-In & Delivery Delay Tracking</div>
        </div>
        <div class="hub-meta">
            <b>Last Upload Time:</b> <span style="color: {time_color}; font-weight: 800;">{st.session_state['upload_time']}</span><br/>
            <b>System Status:</b> <span style="color: #16a34a; font-weight: 800;">● Live Operations</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# Data Processing logic when file is present
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)

        # KPI Calculations
        total_cns = len(df) if "CN_NO" in df.columns else 0
        total_pkg = (
            df["CN_PKG"].sum() if "CN_PKG" in df.columns else df.shape[0]
        )
        total_wt = (
            round(df["CN_WT"].sum() / 1000, 1)
            if "CN_WT" in df.columns
            else 0.0
        )

        over_96 = 0
        avg_aging = 0.0

        if "GATE_IN_AGEING_HRS" in df.columns:
            over_96 = len(df[df["GATE_IN_AGEING_HRS"] > 96])
            avg_aging = round(df["GATE_IN_AGEING_HRS"].mean() / 24, 1)

        # Display Metrics Row
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Total Unique CNs</div><div class="metric-val">{total_cns:,}</div></div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Total CN_PKG (Boxes)</div><div class="metric-val">{total_pkg:,}</div></div>',
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Total Weight (Tonnes)</div><div class="metric-val">{total_wt} T</div></div>',
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">🚨 >96 Hours Pendency</div><div class="metric-val">{over_96:,}</div></div>',
                unsafe_allow_html=True,
            )
        with col5:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Avg Gate-In Aging</div><div class="metric-val">{avg_aging} Days</div></div>',
                unsafe_allow_html=True,
            )

        st.divider()

        # Visualizations Row
        g1, g2 = st.columns(2)

        with g1:
            st.subheader("⏱️ Aging Hours Breakdown (Gate-In)")
            if "GATE_IN_AGEING_HRS" in df.columns:
                bins = [0, 24, 48, 72, 96, 9999]
                labels = [
                    "0-24 Hrs",
                    "24-48 Hrs",
                    "48-72 Hrs",
                    "72-96 Hrs",
                    ">96 Hrs",
                ]
                df["Age_Group"] = pd.cut(
                    df["GATE_IN_AGEING_HRS"], bins=bins, labels=labels
                )
                age_counts = (
                    df["Age_Group"].value_counts().reindex(labels).reset_index()
                )
                age_counts.columns = ["Age Group", "Count"]

                fig1 = px.bar(
                    age_counts,
                    x="Age Group",
                    y="Count",
                    text="Count",
                    color="Count",
                    color_continuous_scale="Reds",
                )
                fig1.update_traces(textposition="outside")
                fig1.update_layout(showlegend=False, height=350)
                st.plotly_chart(fig1, use_container_width=True)

        with g2:
            st.subheader("⚠️ Delay Reasons (UNDLVRD_REASON)")
            if "UNDLVRD_REASON" in df.columns:
                reason_df = (
                    df["UNDLVRD_REASON"]
                    .fillna("No Reason Filled")
                    .value_counts()
                    .head(7)
                    .reset_index()
                )
                reason_df.columns = ["Reason", "Count"]

                fig2 = px.bar(
                    reason_df,
                    y="Reason",
                    x="Count",
                    text="Count",
                    orientation="h",
                    color="Count",
                    color_continuous_scale="Reds",
                )
                fig2.update_traces(textposition="outside")
                fig2.update_layout(
                    showlegend=False, height=350, yaxis=dict(autorange="reverse")
                )
                st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")
