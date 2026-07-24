import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration - Light Clean Dashboard Theme
st.set_page_config(page_title="Floor Ops Dashboard - HubEye Style", layout="wide", initial_sidebar_state="collapsed")

# Delhivery / HubEye Style CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
    }

    .stApp {
        background-color: #f4f6f9;
        color: #1e293b;
    }

    /* Top Navigation / Header Bar */
    .hub-header {
        background-color: #ffffff;
        padding: 16px 28px;
        margin: -4rem -2rem 20px -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .hub-title {
        font-size: 24px !important;
        font-weight: 800;
        color: #d32f2f !important; /* HubEye Red */
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hub-subtitle {
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
    }
    .hub-meta {
        text-align: right;
        font-size: 12px;
        color: #475569;
        line-height: 1.5;
    }

    /* Metric Cards - Clean White Card Style */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        padding: 18px !important;
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
        text-align: left;
    }
    div[data-testid="stMetricValue"] {
        font-size: 30px !important;
        color: #0f172a !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px !important;
        color: #64748b !important;
        text-transform: uppercase;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
    }

    /* Section Subheaders */
    .section-head {
        font-size: 16px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 2px solid #cbd5e1;
    }

    /* Clean Uploader Box */
    div[data-testid="stFileUploader"] {
        background-color: #ffffff;
        border: 2px dashed #cbd5e1;
        border-radius: 8px;
        padding: 10px;
    }

    /* Hide Unwanted UI Overlays */
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

# Top HubEye Style Navigation Header
st.markdown(f"""
    <div class="hub-header">
        <div>
            <div class="hub-title"><span>📦</span> FLOOR OPS | AGING & PENDENCY ANALYTICS</div>
            <div class="hub-subtitle">Kolkata Regional Hubs Pendency Tracking</div>
        </div>
        <div class="hub-meta">
            <b>Last Sync / Upload:</b> <span style="color: #d32f2f; font-weight: 700;">{upload_time_str}</span><br/>
            <b>System Status:</b> <span style="color: #16a34a;">● Live Operations</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Styled Upload Bar
uploaded_file = st.file_uploader("📂 Choose / Upload Operations Data Sheet (.xlsx, .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Live Upload Timestamp
    st.session_state['upload_time'] = datetime.now().strftime("%d-%b-%Y %I:%M %p")
    upload_time_str = st.session_state['upload_time']

    with st.spinner("Processing & Auto-Mapping Columns..."):
        df_raw = pd.read_excel(uploaded_file)
        df_raw.columns = df_raw.columns.str.strip().str.upper()

        # Helper Function to Smartly Find Columns
        def find_column(possible_names, df):
            for name in possible_names:
                for col in df.columns:
                    if name in col:
                        return col
            return None

        # Smart Column Detection
        col_cn = find_column(['CN_CN_NO', 'CN_NO', 'WAYBILL', 'LR_NO', 'CN'], df_raw)
        col_pkg = find_column(['CN_PKG', 'PKG', 'BOX', 'QTY', 'PIECES'], df_raw)
        col_todist = find_column(['TODIST', 'DESTINATION', 'LOCATION', 'HUB'], df_raw)
        col_date = find_column(['CN_DATE', 'BOOKING_DATE', 'DATE'], df_raw)
        col_days = find_column(['CN_TOTAL_DAYS', 'AGEING', 'DAYS', 'PENDING_DAYS'], df_raw)
        col_reason = find_column(['UNDLVRD_REASON', 'REASON', 'REMARKS', 'DELAY_REASON'], df_raw)
        col_mode = find_column(['MODE', 'SERVICE', 'PRIORITY', 'TRANSIT'], df_raw)
        col_cee = find_column(['CEE', 'CONSIGNEE', 'CLIENT', 'RECEIVER'], df_raw)
        col_pin = find_column(['PINCODE', 'PIN_CODE', 'PIN', 'DEST_PIN'], df_raw)

        df = df_raw.copy()

        # 1. Deduplicate by CN / Waybill
        if col_cn:
            df = df.drop_duplicates(subset=[col_cn], keep='first')

        # 2. Filter TODIST Locations
        if col_todist:
            df[col_todist] = df[col_todist].astype(str).str.strip()
            df = df[df[col_todist].isin(ALLOWED_TODIST)]

        # 3. Calculate Exact Aging Days & Hours
        if col_date:
            df['CN_DATE_CLEAN'] = pd.to_datetime(df[col_date], errors='coerce')
            today = pd.to_datetime(datetime.today().date())
            df['CALCULATED_DAYS'] = (today - df['CN_DATE_CLEAN']).dt.days.fillna(0)
            df['CALCULATED_DAYS'] = df['CALCULATED_DAYS'].apply(lambda x: max(0, int(x)))
        elif col_days:
            df['CALCULATED_DAYS'] = pd.to_numeric(df[col_days], errors='coerce').fillna(0).astype(int)
        else:
            df['CALCULATED_DAYS'] = 0

        df['CALCULATED_HOURS'] = df['CALCULATED_DAYS'] * 24

        # 4. Aging Hour Buckets Categorization
        def assign_hour_bucket(hrs):
            if hrs >= 96:
                return "96 Hour Above"
            elif hrs >= 72:
                return "72 Hour Above"
            elif hrs >= 48:
                return "48 Hour Above"
            elif hrs >= 24:
                return "24 Hour Above"
            else:
                return "24 Hour Below"

        df['Aging_Bucket'] = df['CALCULATED_HOURS'].apply(assign_hour_bucket)

        # 5. Precise CN_PKG / Box Calculation
        total_pkg = 0
        if col_pkg:
            total_pkg = pd.to_numeric(df[col_pkg], errors='coerce').fillna(0).sum()

        total_cn = len(df)
        avg_days = round(df['CALCULATED_DAYS'].mean(), 1) if total_cn > 0 else 0

        # KPI Metrics Row
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        
        c1.metric("Total Pending CNs", f"{total_cn:,}")
        c2.metric("Total CN_PKG (Quantity)", f"{int(total_pkg):,}")
        c3.metric("🚨 >96 Hours Pendency", f"{len(df[df['Aging_Bucket']=='96 Hour Above']):,}")
        c4.metric("⚠️ 72-96 Hours Pendency", f"{len(df[df['Aging_Bucket']=='72 Hour Above']):,}")
        c5.metric("Avg Aging (Days)", f"{avg_days} Days")

        st.markdown("<br>", unsafe_allow_html=True)

        # Section 1: Hour Bucket Breakdown & Delivery Reason
        r1_col1, r1_col2 = st.columns(2)

        with r1_col1:
            st.markdown("<div class='section-head'>⏱️ Pendency Breakdown by Hours</div>", unsafe_allow_html=True)
            bucket_order = ["96 Hour Above", "72 Hour Above", "48 Hour Above", "24 Hour Above", "24 Hour Below"]
            bucket_df = df['Aging_Bucket'].value_counts().reindex(bucket_order).fillna(0).reset_index()
            bucket_df.columns = ['Hour Bucket', 'Shipment Count']

            fig_bucket = px.bar(
                bucket_df, x='Hour Bucket', y='Shipment Count', text='Shipment Count',
                color='Hour Bucket',
                color_discrete_map={
                    "96 Hour Above": "#b91c1c",
                    "72 Hour Above": "#ef4444",
                    "48 Hour Above": "#f97316",
                    "24 Hour Above": "#eab308",
                    "24 Hour Below": "#22c55e"
                }
            )
            fig_bucket.update_layout(
                showlegend=False, height=300, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#0f172a', family='Inter')
            )
            st.plotly_chart(fig_bucket, use_container_width=True)

        with r1_col2:
            st.markdown("<div class='section-head'>⚠️ Undelivered / Delay Reasons (UNDLVRD_REASON)</div>", unsafe_allow_html=True)
            if col_reason:
                reason_df = df[col_reason].fillna("No Reason Updated").value_counts().head(7).reset_index()
                reason_df.columns = ['Reason', 'Count']

                fig_reason = px.bar(
                    reason_df, x='Count', y='Reason', orientation='h', text='Count',
                    color='Count', color_continuous_scale='Reds'
                )
                fig_reason.update_layout(
                    showlegend=False, height=300, margin=dict(l=0, r=0, t=10, b=0),
                    yaxis={'categoryorder': 'total ascending'},
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#0f172a', family='Inter')
                )
                st.plotly_chart(fig_reason, use_container_width=True)
            else:
                st.info("Reason column not detected in uploaded sheet.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Section 2: Consignee & Pincode Performance
        r2_col1, r2_col2 = st.columns(2)

        with r2_col1:
            st.markdown("<div class='section-head'>🏢 Consignee Analysis (CEE)</div>", unsafe_allow_html=True)
            if col_cee:
                t1, t2 = st.tabs(["🔥 Top Pending Clients", "📉 Low Pending Clients"])
                with t1:
                    st.dataframe(df[col_cee].value_counts().head(8).reset_index().rename(columns={'index':'Consignee', col_cee:'CN Count'}), use_container_width=True, hide_index=True)
                with t2:
                    st.dataframe(df[col_cee].value_counts().tail(8).reset_index().rename(columns={'index':'Consignee', col_cee:'CN Count'}), use_container_width=True, hide_index=True)

        with r2_col2:
            st.markdown("<div class='section-head'>📍 Pincode Breakdown</div>", unsafe_allow_html=True)
            if col_pin:
                pt1, pt2 = st.tabs(["📍 Top Critical Pincodes", "📌 Low Pending Pincodes"])
                with pt1:
                    st.dataframe(df[col_pin].value_counts().head(8).reset_index().rename(columns={'index':'Pincode', col_pin:'CN Count'}), use_container_width=True, hide_index=True)
                with pt2:
                    st.dataframe(df[col_pin].value_counts().tail(8).reset_index().rename(columns={'index':'Pincode', col_pin:'CN Count'}), use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Section 3: Missing Remarks by Booking Date
        st.markdown("<div class='section-head'>📝 Missing Remarks Tracking (Date-Wise)</div>", unsafe_allow_html=True)
        if col_date and col_reason:
            df['REMARK_STATUS'] = df[col_reason].apply(lambda x: "Missing" if pd.isnull(x) or str(x).strip() == "" or str(x).upper() == "NAN" else "Filled")
            missing_df = df[df['REMARK_STATUS'] == "Missing"]
            
            if len(missing_df) > 0:
                missing_summary = missing_df.groupby(df[col_date].astype(str)).size().reset_index(name='Missing Remarks Count').sort_values(by='Missing Remarks Count', ascending=False)
                st.dataframe(missing_summary, use_container_width=True, hide_index=True)
            else:
                st.success("✅ Remarks are updated for all pending shipments!")

        st.markdown("<br>", unsafe_allow_html=True)

        # Clean Dataset View
        st.markdown("<div class='section-head'>📋 Clean Filtered Operations Table</div>", unsafe_allow_html=True)
        show_cols = [c for c in [col_cn, col_todist, col_date, col_mode, col_cee, col_pin, col_pkg, col_reason] if c]
        
        display_df = df[show_cols + ['CALCULATED_DAYS', 'Aging_Bucket']].sort_values(by='CALCULATED_DAYS', ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Download Cleaned CSV
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Filtered Hub Data (CSV)", data=csv_data, file_name="Floor_Ops_HubEye_Report.csv", mime="text/csv")
