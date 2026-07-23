import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration & Styling
st.set_page_config(page_title="Warehouse Analytics Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric {
        background: #1e222d;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00d26a;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #ffffff; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-size: 14px; color: #a0aab8; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Warehouse Aging & Client Performance Analytics")
st.write("Upload your warehouse stock file to get instant insights, client-wise breakdowns, and region distribution.")

uploaded_file = st.file_uploader("Upload Excel File (.xlsx, .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    with st.spinner("Processing data..."):
        df = pd.read_excel(uploaded_file)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Calculate Accurate CN Total Days
        if 'CN_DATE' in df.columns:
            df['CN_DATE_CLEAN'] = pd.to_datetime(df['CN_DATE'], errors='coerce')
            today = pd.to_datetime(datetime.today().date())
            df['CALCULATED_DAYS'] = (today - df['CN_DATE_CLEAN']).dt.days.fillna(df.get('CN_TOTAL_DAYS', 0))
        else:
            df['CALCULATED_DAYS'] = df.get('CN_TOTAL_DAYS', 0)
            
        df['CALCULATED_DAYS'] = df['CALCULATED_DAYS'].apply(lambda x: max(0, int(x)) if pd.notnull(x) else 0)

        # Aging Buckets
        def get_bucket(days):
            if days <= 30: return "0-30 Days"
            elif days <= 90: return "31-90 Days"
            else: return "> 90 Days (Critical)"

        df['Aging_Bucket'] = df['CALCULATED_DAYS'].apply(get_bucket)

        # Metrics
        total_cases = len(df)
        avg_aging = round(df['CALCULATED_DAYS'].mean(), 1)
        critical_cases = len(df[df['CALCULATED_DAYS'] > 90])
        mid_cases = len(df[(df['CALCULATED_DAYS'] > 30) & (df['CALCULATED_DAYS'] <= 90)])
        fresh_cases = len(df[df['CALCULATED_DAYS'] <= 30])

        # KPI Cards Display
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Pending Stock", f"{total_cases:,}")
        c2.metric("Fresh Stock (0-30 Days)", f"{fresh_cases:,}")
        c3.metric("Medium Aging (31-90 Days)", f"{mid_cases:,}")
        c4.metric("🚨 Critical (>90 Days)", f"{critical_cases:,}")
        c5.metric("Avg Aging Days", f"{avg_aging} Days")

        st.divider()

        # Section 1: Top Clients Analysis & Region Buckets
        col_left, col_right = st.columns(2)

        client_col = 'CEE' if 'CEE' in df.columns else 'CONSIGNEE' if 'CONSIGNEE' in df.columns else None
        region_col = 'FROMSOURCE' if 'FROMSOURCE' in df.columns else 'REGION' if 'REGION' in df.columns else None

        with col_left:
            st.subheader("🏢 Top 10 Clients by Pending Cases")
            if client_col:
                top_clients = df[client_col].value_counts().head(10).reset_index()
                top_clients.columns = ['Client Name', 'Total Cases']
                fig_client = px.bar(top_clients, x='Total Cases', y='Client Name', orientation='h', 
                                    text='Total Cases', color='Total Cases', color_continuous_scale='Blues')
                fig_client.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=20, b=0), height=350)
                st.plotly_chart(fig_client, use_container_width=True)
            else:
                st.info("Client column not found in Excel.")

        with col_right:
            st.subheader("📍 Region / Source Aging Breakdown")
            if region_col:
                region_summary = df.groupby([region_col, 'Aging_Bucket']).size().unstack(fill_value=0)
                st.dataframe(region_summary, use_container_width=True, height=350)
            else:
                st.info("Region/Source column not found in Excel.")

        st.divider()

        # Section 2: Critical Cases Table
        st.subheader("⚠️ Top Critical Cases (> 30 Days Aging)")
        critical_df = df[df['CALCULATED_DAYS'] > 30].sort_values(by='CALCULATED_DAYS', ascending=False)
        
        display_cols = [c for c in ['CN_CN_NO', client_col, region_col, 'CN_DATE', 'CALCULATED_DAYS', 'UNDLVRD_REASON', 'CN_REMARKS'] if c and c in df.columns]
        
        st.dataframe(critical_df[display_cols].rename(columns={'CALCULATED_DAYS': 'Calculated Aging (Days)'}), use_container_width=True)

        # Download Export
        st.divider()
        csv = critical_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Critical Cases Data (CSV)", data=csv, file_name='Critical_Warehouse_Cases.csv', mime='text/csv')
