import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Om Logistics Warehouse Report", layout="wide", initial_sidebar_state="collapsed")

# Om Logistics Corporate Branding Theme CSS
st.markdown("""
    <style>
    /* Base App Theme */
    .stApp {
        background-color: #0d1321;
        color: #ffffff;
    }
    
    /* Om Logistics Header Style */
    .om-header {
        background: linear-gradient(135deg, #b91c1c 0%, #1e293b 100%);
        padding: 22px 30px;
        color: white;
        margin: -4rem -2rem 25px -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 3px solid #ef4444;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .om-title { 
        font-size: 28px !important; 
        font-weight: 800; 
        color: #ffffff !important; 
        text-transform: uppercase; 
        letter-spacing: 1px;
    }
    .om-subtitle { font-size: 14px; color: #fca5a5; margin-top: 2px; font-weight: 500; }
    .om-right { text-align: right; font-size: 13px; color: #ffffff; line-height: 1.6; }

    /* Custom Metric Cards with High Contrast */
    div[data-testid="stMetric"] {
        background: #1e293b !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border-top: 4px solid #ef4444 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
        text-align: center;
    }
    div[data-testid="stMetricValue"] { 
        font-size: 34px !important; 
        color: #ffffff !important; 
        font-weight: 800 !important; 
    }
    div[data-testid="stMetricLabel"] { 
        font-size: 13px !important; 
        color: #cbd5e1 !important; 
        text-transform: uppercase; 
        font-weight: 700 !important; 
    }

    /* Tabs & Tables visibility fix */
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { color: #ffffff !important; font-weight: 600; }
    
    /* Hide Streamlit Default Toolbars */
    header { visibility: hidden; display: none !important; }
    footer { visibility: hidden; display: none !important; }
    #MainMenu { visibility: hidden; display: none !important; }
    [data-testid="stHeader"] { visibility: hidden; display: none !important; }
    [data-testid="stAppToolbar"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .viewerBadge_container__1S-5D, .viewerBadge_link__1S-5D { display: none !important; }
    #stDecoration { display: none !important; }
    div[class*="viewerBadge"] { display: none !important; }
    div[class*="styles_viewerBadge"] { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# List of Specified TODIST Locations
ALLOWED_TODIST = [
    "DHULAGARH HUB KOLKATA",
    "DANKUNI KOLKATA-WEST BANGAL",
    "HOWRAH KOLKATA-WEST BANGAL",
    "CHANDANI CHAWK-KOLKATA",
    "WEST BENGAL HIDE ROAD KMA",
    "DUNLOP KOLKATA-WEST BANGAL",
    "KOLKATA AIRPORT",
    "TATA MOTORS LTD (SPD) KOLKATA",
    "VE COMMERCIAL SPD KOLKATA",
    "M D ROAD (BADA BAZAR)  BA",
    "M D ROAD (BADA BAZAR) BA",
    "KOLKATA CENTRAL-WEST BANGAL",
    "HOWRAH STATION - WEST BANGAL"
]

# Track Upload Timestamp
upload_time_str = st.session_state.get('upload_time', "Not Uploaded Yet")

# Header Rendering
st.markdown(f"""
    <div class="om-header">
        <div>
            <div class="om-title">🚛 OM LOGISTICS LIMITED</div>
            <div class="om-subtitle">Warehouse Aging & Stock Analytics Dashboard</div>
        </div>
        <div class="om-right">
            <b>Region:</b> Kolkata / West Bengal Hubs<br/>
            <b>File Upload Time:</b> <span style="color: #fca5a5;">{upload_time_str}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Styled Upload Area
uploaded_file = st.file_uploader("📂 Select / Upload Warehouse Excel File (.xlsx, .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Set Live Time on Upload
    st.session_state['upload_time'] = datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
    upload_time_str = st.session_state['upload_time']

    with st.spinner("Cleaning Duplicate CNs & Filtering TODIST Locations..."):
        raw_df = pd.read_excel(uploaded_file)
        
        # Clean column names spaces
        raw_df.columns = raw_df.columns.str.strip()

        # Helper to safely select column by Index
        def get_col_by_idx(df, idx):
            if idx < len(df.columns):
                return df.columns[idx]
            return None

        # Column Mapping
        col_a = get_col_by_idx(raw_df, 0)   # Col A (CN_CN_NO)
        col_b = get_col_by_idx(raw_df, 1)   # Col B
        col_c = get_col_by_idx(raw_df, 2)   # Col C (Mode / Priority)
        col_d = get_col_by_idx(raw_df, 3)   # Col D
        col_e = get_col_by_idx(raw_df, 4)   # Col E
        col_f = get_col_by_idx(raw_df, 5)   # Col F
        col_g = get_col_by_idx(raw_df, 6)   # Col G (TODIST Location)
        col_i = get_col_by_idx(raw_df, 8)   # Col I (CN Date)
        col_j = get_col_by_idx(raw_df, 9)   # Col J (CEE / Consignee)
        col_l = get_col_by_idx(raw_df, 11)  # Col L (Pincode)
        col_m = get_col_by_idx(raw_df, 12)  # Col M (CN_PKG / Boxes)
        col_aq = get_col_by_idx(raw_df, 42) # Col AQ (Reason / Remarks)

        df = raw_df.copy()

        # 1. REMOVE DUPLICATE CN NUMBERS (Col A)
        if col_a and col_a in df.columns:
            df = df.drop_duplicates(subset=[col_a], keep='first')

        # 2. FILTER BY TODIST LOCATIONS (Col G)
        if col_g and col_g in df.columns:
            df[col_g] = df[col_g].astype(str).str.strip()
            df = df[df[col_g].isin(ALLOWED_TODIST)]

        # 3. ACCURATE AGING DAYS CALCULATION (Col I)
        if col_i and col_i in df.columns:
            df['CN_DATE_CLEAN'] = pd.to_datetime(df[col_i], errors='coerce')
            today = pd.to_datetime(datetime.today().date())
            df['CALCULATED_DAYS'] = (today - df['CN_DATE_CLEAN']).dt.days.fillna(0)
            df['CALCULATED_DAYS'] = df['CALCULATED_DAYS'].apply(lambda x: max(0, int(x)))
        else:
            df['CALCULATED_DAYS'] = 0

        # 4. ACCURATE CN_PKG / TOTAL BOXES SUM (Col M)
        total_boxes = 0
        if col_m and col_m in df.columns:
            total_boxes = pd.to_numeric(df[col_m], errors='coerce').fillna(0).sum()

        # Metrics Values
        total_cases = len(df)
        critical_cases = len(df[df['CALCULATED_DAYS'] > 90])
        avg_aging = round(df['CALCULATED_DAYS'].mean(), 1) if len(df) > 0 else 0

        st.markdown("---")

        # KPI Metrics Summary Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Pending Shipments (Unique CN)", f"{total_cases:,}")
        c2.metric("Total CN_PKG (Total Boxes)", f"{int(total_boxes):,}")
        c3.metric("🚨 Critical Aging (>90 Days)", f"{critical_cases:,}")
        c4.metric("Avg Aging Days", f"{avg_aging} Days")

        st.markdown("<br>", unsafe_allow_html=True)

        # Mode Breakdown & Delivery Reasons
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            st.subheader("✈️ Transit Mode Breakdown (Col C)")
            if col_c and col_c in df.columns:
                mode_counts = df[col_c].value_counts().reset_index()
                mode_counts.columns = ['Mode', 'Count']
                fig_mode = px.pie(mode_counts, names='Mode', values='Count', hole=0.4,
                                  color_discrete_sequence=px.colors.qualitative.Bold)
                fig_mode.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig_mode, use_container_width=True)

        with row1_col2:
            st.subheader("⚠️ Delivery Delay Reasons (Col AQ)")
            if col_aq and col_aq in df.columns:
                reason_counts = df[col_aq].fillna("No Reason Provided").value_counts().head(8).reset_index()
                reason_counts.columns = ['Reason', 'Count']
                fig_reason = px.bar(reason_counts, x='Count', y='Reason', orientation='h', text='Count',
                                    color='Count', color_continuous_scale='Reds')
                fig_reason.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=30, b=0), height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig_reason, use_container_width=True)

        st.markdown("---")

        # Clients & Pin Codes
        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            st.subheader("🏢 Consignee Analysis (CEE - Col J)")
            if col_j and col_j in df.columns:
                tab1, tab2 = st.tabs(["🔥 Top Pending Clients", "📉 Low Pending Clients"])
                with tab1:
                    top_clients = df[col_j].value_counts().head(10).reset_index()
                    top_clients.columns = ['Client Name', 'Total Cases']
                    st.dataframe(top_clients, use_container_width=True, hide_index=True)
                with tab2:
                    low_clients = df[col_j].value_counts().tail(10).reset_index()
                    low_clients.columns = ['Client Name', 'Total Cases']
                    st.dataframe(low_clients, use_container_width=True, hide_index=True)

        with row2_col2:
            st.subheader("📍 Pin Code Summary (Col L)")
            if col_l and col_l in df.columns:
                tab_p1, tab_p2 = st.tabs(["📍 Top Critical Pin Codes", "📌 Low Pending Pin Codes"])
                with tab_p1:
                    top_pins = df[col_l].value_counts().head(10).reset_index()
                    top_pins.columns = ['Pin Code', 'Total Cases']
                    st.dataframe(top_pins, use_container_width=True, hide_index=True)
                with tab_p2:
                    low_pins = df[col_l].value_counts().tail(10).reset_index()
                    low_pins.columns = ['Pin Code', 'Total Cases']
                    st.dataframe(low_pins, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Missing Remarks Tracking Date-wise
        st.subheader("📝 Missing Remarks Tracking (Date-wise)")
        if col_i and col_aq and col_i in df.columns and col_aq in df.columns:
            df['REMARKS_STATUS'] = df[col_aq].apply(lambda x: "Filled" if pd.notnull(x) and str(x).strip() != "" else "Missing Remarks")
            missing_df = df[df['REMARKS_STATUS'] == "Missing Remarks"]
            
            if len(missing_df) > 0:
                missing_by_date = missing_df.groupby(missing_df[col_i].astype(str)).size().reset_index(name='Missing Remarks Count')
                missing_by_date = missing_by_date.sort_values(by='Missing Remarks Count', ascending=False)
                st.dataframe(missing_by_date, use_container_width=True, hide_index=True)
            else:
                st.success("All pending shipments have remarks filled!")

        st.markdown("---")

        # Table Display
        st.subheader("📋 Clean Filtered Dataset (Selected Columns & Unique CN)")
        target_cols = [c for c in [col_a, col_b, col_c, col_d, col_e, col_f, col_g, col_i, col_j, col_l, col_m, col_aq] if c and c in df.columns]
        
        filtered_df = df[target_cols + ['CALCULATED_DAYS']].sort_values(by='CALCULATED_DAYS', ascending=False)
        st.dataframe(filtered_df.rename(columns={'CALCULATED_DAYS': 'Calculated Aging (Days)'}), use_container_width=True, hide_index=True)

        # Export CSV Button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Cleaned Report (CSV)", data=csv, file_name='OmLogistics_Cleaned_Report.csv', mime='text/csv')
