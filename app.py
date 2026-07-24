import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Warehouse Aging Report", layout="wide", initial_sidebar_state="collapsed")

# Complete Executive Theme & Clean UI Styling
st.markdown("""
    <style>
    /* Page Background */
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    
    /* Header Bar */
    .custom-header {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        padding: 22px 30px;
        color: white;
        margin: -4rem -2rem 25px -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #334155;
    }
    .header-title { font-size: 26px !important; font-weight: 700; color: #f8fafc !important; text-transform: uppercase; letter-spacing: 0.5px; }
    .header-subtitle { font-size: 14px; color: #94a3b8; margin-top: 2px; }
    .header-right { text-align: right; font-size: 13px; color: #cbd5e1; line-height: 1.5; }

    /* File Uploader Container Box */
    div[data-testid="stFileUploader"] {
        background-color: #1e293b;
        border: 2px dashed #3b82f6;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* KPI Cards */
    div[data-testid="stMetric"] {
        background: #1e293b;
        padding: 20px !important;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 15px;
        text-align: center;
    }
    div[data-testid="stMetricValue"] { font-size: 32px !important; color: #38bdf8 !important; font-weight: 700 !important; }
    div[data-testid="stMetricLabel"] { font-size: 13px !important; color: #94a3b8 !important; text-transform: uppercase; font-weight: 600; }

    /* Hide Streamlit Overlays, GitHub & Bottom Watermarks */
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

# Executive Header
current_date_str = datetime.today().strftime("%B %Y")

st.markdown(f"""
    <div class="custom-header">
        <div>
            <div class="header-title">Warehouse Aging & Shipment Analytics</div>
            <div class="header-subtitle">Live Aging, Transport Mode, Client & Pin Code Insights</div>
        </div>
        <div class="header-right">
            <b>Report Date:</b> {current_date_str}<br/>
            <b>Department:</b> Warehouse & Logistics Ops
        </div>
    </div>
""", unsafe_allow_html=True)

# Styled Upload Area
uploaded_file = st.file_uploader("📂 Drop or Select Warehouse Excel File (.xlsx, .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    with st.spinner("Analyzing Logistics Data..."):
        # Load Excel File
        raw_df = pd.read_excel(uploaded_file)
        
        # Helper to safely select column by Index (A=0, B=1, C=2...)
        def get_col_by_idx(df, idx):
            if idx < len(df.columns):
                return df.columns[idx]
            return None

        # Map Excel Columns
        col_a = get_col_by_idx(raw_df, 0)   # Col A
        col_b = get_col_by_idx(raw_df, 1)   # Col B
        col_c = get_col_by_idx(raw_df, 2)   # Col C (Mode / Priority: Air, Speed, Train)
        col_d = get_col_by_idx(raw_df, 3)   # Col D
        col_e = get_col_by_idx(raw_df, 4)   # Col E
        col_f = get_col_by_idx(raw_df, 5)   # Col F
        col_g = get_col_by_idx(raw_df, 6)   # Col G
        # Col H (idx 7) is intentionally skipped
        col_i = get_col_by_idx(raw_df, 8)   # Col I (CN Date / Aging Date)
        col_j = get_col_by_idx(raw_df, 9)   # Col J (CEE / Consignee)
        col_l = get_col_by_idx(raw_df, 11)  # Col L (Pincode)
        col_m = get_col_by_idx(raw_df, 12)  # Col M (Box / Quantity Count)
        col_aq = get_col_by_idx(raw_df, 42) # Col AQ (Undelivered Reason / Remarks)

        # Copy data
        df = raw_df.copy()

        # Calculate Aging Days based on Col I (CN Date)
        if col_i and col_i in df.columns:
            df['CN_DATE_CLEAN'] = pd.to_datetime(df[col_i], errors='coerce')
            today = pd.to_datetime(datetime.today().date())
            df['CALCULATED_DAYS'] = (today - df['CN_DATE_CLEAN']).dt.days.fillna(0)
            df['CALCULATED_DAYS'] = df['CALCULATED_DAYS'].apply(lambda x: max(0, int(x)))
        else:
            df['CALCULATED_DAYS'] = 0

        # Calculate Total Boxes (Col M)
        total_boxes = 0
        if col_m and col_m in df.columns:
            total_boxes = pd.to_numeric(df[col_m], errors='coerce').fillna(0).sum()

        # KPI Metrics Display
        total_cases = len(df)
        critical_cases = len(df[df['CALCULATED_DAYS'] > 90])
        avg_aging = round(df['CALCULATED_DAYS'].mean(), 1) if len(df) > 0 else 0

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Pending Shipments", f"{total_cases:,}")
        c2.metric("Total Boxes / Quantity", f"{int(total_boxes):,}")
        c3.metric("🚨 Critical Aging (>90 Days)", f"{critical_cases:,}")
        c4.metric("Avg Aging Days", f"{avg_aging} Days")

        st.markdown("<br>", unsafe_allow_html=True)

        # SECTION 1: Mode Analysis (Col C) & Undelivered Reasons (Col AQ)
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            st.subheader("✈️ Transit Mode Breakdown (Air / Speed / Train)")
            if col_c and col_c in df.columns:
                mode_counts = df[col_c].value_counts().reset_index()
                mode_counts.columns = ['Mode', 'Shipment Count']
                fig_mode = px.pie(mode_counts, names='Mode', values='Shipment Count', hole=0.4,
                                  color_discrete_sequence=px.colors.qualitative.Set2)
                fig_mode.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=320)
                st.plotly_chart(fig_mode, use_container_width=True)
            else:
                st.info("Mode column (Col C) not found.")

        with row1_col2:
            st.subheader("⚠️ Undelivered / Delay Reasons Summary (Col AQ)")
            if col_aq and col_aq in df.columns:
                reason_counts = df[col_aq].fillna("No Reason Provided").value_counts().head(8).reset_index()
                reason_counts.columns = ['Reason', 'Count']
                fig_reason = px.bar(reason_counts, x='Count', y='Reason', orientation='h', text='Count',
                                    color='Count', color_continuous_scale='Reds')
                fig_reason.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=30, b=0), height=320)
                st.plotly_chart(fig_reason, use_container_width=True)
            else:
                st.info("Reason column (Col AQ) not found.")

        st.markdown("---")

        # SECTION 2: Top & Low Clients (Col J) and Pin Codes (Col L)
        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            st.subheader("🏢 Clients Analysis (CEE - Col J)")
            if col_j and col_j in df.columns:
                tab1, tab2 = st.tabs(["🔥 Top 10 High Pending", "📉 Low Pending Clients"])
                with tab1:
                    top_clients = df[col_j].value_counts().head(10).reset_index()
                    top_clients.columns = ['Client Name', 'Total Cases']
                    st.dataframe(top_clients, use_container_width=True, hide_index=True)
                with tab2:
                    low_clients = df[col_j].value_counts().tail(10).reset_index()
                    low_clients.columns = ['Client Name', 'Total Cases']
                    st.dataframe(low_clients, use_container_width=True, hide_index=True)

        with row2_col2:
            st.subheader("📍 Pin Code Performance (Col L)")
            if col_l and col_l in df.columns:
                tab_p1, tab_p2 = st.tabs(["📍 Top 10 Critical Pin Codes", "📌 Low Pending Pin Codes"])
                with tab_p1:
                    top_pins = df[col_l].value_counts().head(10).reset_index()
                    top_pins.columns = ['Pin Code', 'Total Cases']
                    st.dataframe(top_pins, use_container_width=True, hide_index=True)
                with tab_p2:
                    low_pins = df[col_l].value_counts().tail(10).reset_index()
                    low_pins.columns = ['Pin Code', 'Total Cases']
                    st.dataframe(low_pins, use_container_width=True, hide_index=True)

        st.markdown("---")

        # SECTION 3: Missing Remarks by Date Tracking
        st.subheader("📝 Missing Remarks Tracking (Date-wise)")
        if col_i and col_aq and col_i in df.columns and col_aq in df.columns:
            # Check empty or blank remarks
            df['REMARKS_FILLED'] = df[col_aq].apply(lambda x: "Filled" if pd.notnull(x) and str(x).strip() != "" else "Missing Remarks")
            missing_df = df[df['REMARKS_FILLED'] == "Missing Remarks"]
            
            if col_i in missing_df.columns:
                missing_by_date = missing_df.groupby(missing_df[col_i].astype(str)).size().reset_index(name='Missing Remarks Count')
                missing_by_date = missing_by_date.sort_values(by='Missing Remarks Count', ascending=False)
                st.dataframe(missing_by_date, use_container_width=True, hide_index=True)
            else:
                st.write("All remarks are properly updated!")

        st.markdown("---")

        # SECTION 4: Selected Filtered Excel Columns Data Table
        st.subheader("📋 Selected Filtered Stock Table (A, B, C, D, E, F, G, I, J, L, M, AQ)")
        
        # Include specified columns + Calculated Aging
        target_cols = [c for c in [col_a, col_b, col_c, col_d, col_e, col_f, col_g, col_i, col_j, col_l, col_m, col_aq] if c and c in df.columns]
        
        filtered_df = df[target_cols + ['CALCULATED_DAYS']].sort_values(by='CALCULATED_DAYS', ascending=False)
        
        st.dataframe(filtered_df.rename(columns={'CALCULATED_DAYS': 'Calculated Aging (Days)'}), use_container_width=True, hide_index=True)

        # Export Data Button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Selected Filtered Report (CSV)", data=csv, file_name='Filtered_Warehouse_Report.csv', mime='text/csv')
