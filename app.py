import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Warehouse Aging Report", layout="wide", initial_sidebar_state="collapsed")

# Styling - Fix Header Cut-off & Create Clean UI
st.markdown("""
    <style>
    /* 1. Page Background */
    .stApp {
        background-color: #f7f9fb;
    }
    
    /* 2. Header Bar Styling (Fixed Margin so it doesn't cut) */
    .custom-header {
        background-color: #0c1830;
        padding: 20px 30px;
        color: white;
        margin: -4rem -2rem 20px -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #1a2c4e;
    }
    .header-title { font-size: 26px !important; font-weight: 700; color: white !important; margin-bottom: 4px; text-transform: uppercase; }
    .header-subtitle { font-size: 14px; color: #a0b0d0; }
    .header-right { text-align: right; font-size: 13px; color: #ffffff; line-height: 1.5; }

    /* 3. Executive KPI Cards */
    div[data-testid="stMetric"] {
        background: #ffffff;
        padding: 20px !important;
        border-radius: 8px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 15px;
        text-align: center;
    }
    div[data-testid="stMetricValue"] {
        font-size: 34px !important;
        color: #0d265a !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #57606a !important;
        text-transform: uppercase;
        font-weight: 600;
    }

    /* 4. Hide Top Streamlit Toolbar & GitHub Branding */
    header { visibility: hidden; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    [data-testid="stHeader"] { visibility: hidden; }
    [data-testid="stAppToolbar"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# Executive Header
current_date_str = datetime.today().strftime("%B %Y")

st.markdown(f"""
    <div class="custom-header">
        <div>
            <div class="header-title">Warehouse Aging Report</div>
            <div class="header-subtitle">Pending Stock & Oldest Unresolved Cases Summary</div>
        </div>
        <div class="header-right">
            <b>Report Date:</b> {current_date_str}<br/>
            <b>Department:</b> Warehouse & Logistics Ops
        </div>
    </div>
""", unsafe_allow_html=True)

# 5. Simple File Uploader right at the top
uploaded_file = st.file_uploader("📂 Select / Upload Warehouse Excel File (.xlsx, .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    with st.spinner("Processing warehouse data..."):
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

        st.markdown("---")

        # KPI Cards Display
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Pending Stock", f"{total_cases:,}")
        c2.metric("Fresh Stock (0-30 Days)", f"{fresh_cases:,}")
        c3.metric("🚨 Critical Stock (>90 Days)", f"{critical_cases:,}")
        c4.metric("Avg Aging Days", f"{avg_aging} Days")

        st.markdown("<br>", unsafe_allow_html=True)

        # Top Clients & Region Breakdown
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
                fig_client.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=20, b=0), height=320)
                st.plotly_chart(fig_client, use_container_width=True)

        with col_right:
            st.subheader("📍 Region / Source Aging Breakdown")
            if region_col:
                region_summary = df.groupby([region_col, 'Aging_Bucket']).size().unstack(fill_value=0)
                st.dataframe(region_summary, use_container_width=True, height=320)

        # Critical Cases Table
        st.subheader("⚠️ Top Critical Cases (> 30 Days Aging)")
        critical_df = df[df['CALCULATED_DAYS'] > 30].sort_values(by='CALCULATED_DAYS', ascending=False)
        
        display_cols = [c for c in ['CN_CN_NO', client_col, region_col, 'CN_DATE', 'CALCULATED_DAYS', 'UNDLVRD_REASON', 'CN_REMARKS'] if c and c in df.columns]
        
        st.dataframe(critical_df[display_cols].rename(columns={
            'CALCULATED_DAYS': 'Aging (Days)',
            'CN_CN_NO': 'CN Number',
            client_col: 'Consignee (Client)',
            region_col: 'From / Region',
            'CN_DATE': 'CN Date',
            'UNDLVRD_REASON': 'Delay Reason',
            'CN_REMARKS': 'Remarks'
        }), use_container_width=True, hide_index=True)

        # Export Button
        csv = critical_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Critical Cases Data (CSV)", data=csv, file_name='Critical_Warehouse_Cases.csv', mime='text/csv')
