import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="LOGISTICS AGING CASES DASHBOARD", layout="wide", initial_sidebar_state="expanded")

# Complete Premium Corporate UI Styling - Matching image_8.png
st.markdown("""
    <style>
    /* 1. Page Background to Light Grey */
    .stApp {
        background-color: #f7f9fb;
    }
    
    /* 2. Custom Executive Header Bar (Navy Blue) */
    .custom-header {
        background-color: #0c1830;
        padding: 20px 30px;
        color: white;
        margin: -95px -2rem 0px -2rem; /* Pull up to the very top */
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #1a2c4e;
    }
    .header-left { flex-grow: 1; }
    .header-title { font-size: 26px !important; font-weight: 700; color: white !important; margin-bottom: 5px; text-transform: uppercase; }
    .header-subtitle { font-size: 16px; color: #a0b0d0; }
    .header-right { text-align: right; font-size: 14px; color: white; line-height: 1.5; }

    /* 3. Pure White, Flat KPI Cards with Top Shadow & Border */
    div[data-testid="stMetric"] {
        background: #ffffff;
        padding: 25px !important;
        border-radius: 6px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        text-align: center;
    }
    div[data-testid="stMetricValue"] {
        font-size: 38px !important;
        color: #0d265a !important; /* Premium Navy Blue for numbers */
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #6a737d !important;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Highlight special KPI with Red (matches image_8.png second card) */
    div[data-testid="stMetric"]:nth-child(2) div[data-testid="stMetricValue"] {
        color: #d11313 !important;
    }

    /* 4. Subheader Styles */
    h3 {
        color: #0d265a !important;
        font-weight: 600 !important;
        font-size: 20px !important;
        padding-top: 20px;
        margin-bottom: 15px;
    }
    
    /* 5. Cleanup Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e1e4e8;
    }
    [data-testid="stSidebarNav"] { padding-top: 15px; }
    
    /* 6. Main Content Area Padding */
    .block-container {
        padding-top: 40px !important;
    }
    
    /* 7. Hide Streamlit Overlays & GitHub/Fork Icons */
    header { visibility: hidden; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    [data-testid="stHeader"] { visibility: hidden; }
    [data-testid="stAppToolbar"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# Define Current Data Date for Header
current_date_str = datetime.today().strftime("%B %Y") # e.g., "July 2026"

# Create the Custom Executive Header Bar
st.markdown(f"""
    <div class="custom-header">
        <div class="header-left">
            <div class="header-title">Warehouse Aging Report</div>
            <div class="header-subtitle">Pending Stock & Oldest Unresolved Cases Summary</div>
        </div>
        <div class="header-right">
            Report Date: {current_date_str}<br/>
            Department: Warehouse & Logistics Ops
        </div>
    </div>
""", unsafe_allow_html=True)

# 8. Move File Uploader to Sidebar
st.sidebar.subheader("Data Upload")
uploaded_file = st.sidebar.file_uploader("Choose Warehouse Excel File (.xlsx, .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    # 9. Main Area for Dashboard Content (visible only after upload)
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

        # KPI Cards Display - Four Cards Matching image_8.png
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Pending Stock", f"{total_cases:,}")
        c2.metric("Critical Cases (>90 Days)", f"{critical_cases:,}")
        c3.metric("Avg Aging Days", f"{avg_aging} Days")
        
        # New KPI based on image_8.png: Total Cases with some Aging (> 30 Days)
        aging_total_cases = critical_cases + mid_cases
        c4.metric("Aging over 30 Days", f"{aging_total_cases:,}")

        # Section: Clean Data Display
        st.subheader("⚠️ Top Critical Cases (> 30 Days Aging)")
        critical_df = df[df['CALCULATED_DAYS'] > 30].sort_values(by='CALCULATED_DAYS', ascending=False)
        
        # Define columns for a clean view, matching the spirit of the data table in image_8.png
        client_col = 'CEE' if 'CEE' in df.columns else 'CONSIGNEE' if 'CONSIGNEE' in df.columns else None
        region_col = 'FROMSOURCE' if 'FROMSOURCE' in df.columns else 'REGION' if 'REGION' in df.columns else None
        
        display_cols = [c for c in ['CN_CN_NO', client_col, region_col, 'CN_DATE', 'CALCULATED_DAYS', 'UNDLVRD_REASON', 'CN_REMARKS'] if c and c in df.columns]
        
        # Display the data table with premium formatting
        st.dataframe(critical_df[display_cols].rename(columns={
            'CALCULATED_DAYS': 'Aging (Days)',
            'CN_CN_NO': 'CN Number',
            client_col: 'Consignee (Client)',
            region_col: 'From / Region',
            'CN_DATE': 'CN Date',
            'UNDLVRD_REASON': 'Delay Reason',
            'CN_REMARKS': 'Remarks'
        }), use_container_width=True, hide_index=True)

        # Download Export
        st.markdown("<br>", unsafe_allow_html=True)
        csv = critical_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Critical Cases Data (CSV)", data=csv, file_name='Critical_Warehouse_Cases.csv', mime='text/csv')

else:
    # Instruction for user if no file is uploaded
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("Please upload your warehouse Excel file using the sidebar on the left.")
