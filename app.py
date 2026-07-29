import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration - Clean Dashboard
st.set_page_config(page_title="Floor Ops Dashboard - Om Logistics", layout="wide")

# Complete Black & Bold Text Styling CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        color: #000000 !important;
    }

    .stApp {
        background-color: #f4f6f9;
    }

    /* Top Navigation / Header Bar */
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

    /* Metric Cards - Bold Black Font */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        padding: 18px !important;
        border-radius: 8px !important;
        border: 2px solid #cbd5e1 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        text-align: left;
    }
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        color: #000000 !important;
        font-weight: 900 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #000000 !important;
        text-transform: uppercase;
        font-weight: 800 !important;
        letter-spacing: 0.5px;
    }

    /* Section Subheaders */
    .section-head {
        font-size: 18px;
        font-weight: 900;
        color: #000000;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 3px solid #d32f2f;
    }

    /* Table text styling - All Bold Black */
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Clean Uploader Box */
    div[data-testid="stFileUploader"] {
        background-color: #ffffff;
        border: 2px dashed #94a3b8;
        border-radius: 8px;
        padding: 10px;
    }

    /* Tabs Adjustment */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        padding-top: 0px;
        padding-bottom: 0px;
        font-weight: 800 !important;
    }

    /* Radio buttons styling for date picker */
    div[role="radiogroup"] {
        flex-direction: row !important;
        gap: 12px;
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

# Top Navigation Header
st.markdown("""
    <div class="hub-header">
        <div>
            <div class="hub-title"><span>🚛</span> FLOOR OPS | AGING & PENDENCY ANALYTICS</div>
            <div class="hub-subtitle">Kolkata Regional Hubs - Gate-In & Delivery Delay Tracking</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Helper Function to Format Weight smartly into Ton or KG
def format_weight(kg_val):
    if kg_val >= 1000:
        return f"{kg_val / 1000:.2f} Ton"
    else:
        return f"{kg_val:.1f} KG"

# Session State Initialization
if "processed_df" not in st.session_state:
    st.session_state["processed_df"] = None

# --- STEP 1: FILE UPLOADER (TOP) ---
uploaded_file = st.file_uploader("Upload Operations Excel Sheet (.xlsx, .xls)", type=["xlsx", "xls"])

# Process File if Uploaded
if uploaded_file is not None:
    with st.spinner("Processing Operations Data & Removing Duplicates..."):
        df_raw = pd.read_excel(uploaded_file)
        df_raw.columns = df_raw.columns.str.strip().str.upper()

        # Helper Function to Smartly Find Columns
        def find_column(possible_names, df):
            for name in possible_names:
                for col in df.columns:
                    if name in col:
                        return col
            return None

        # Smart Column Mapping
        col_cn = find_column(['CN_CN_NO', 'CN_NO', 'WAYBILL', 'LR_NO', 'CN'], df_raw)
        col_pkg = find_column(['CN_PKG', 'PKG', 'BOX', 'QTY', 'PIECES'], df_raw)
        col_wt = find_column(['ACT_WT', 'CHG_WT', 'WT', 'WEIGHT', 'TOTAL_WEIGHT', 'KGS'], df_raw)
        col_todist = find_column(['TODIST', 'DESTINATION', 'LOCATION', 'HUB'], df_raw)
        col_gatein_date = find_column(['CHLN_GATE_IN_DATE', 'GATE_IN_DATE', 'GATE_IN', 'GATEIN'], df_raw)
        col_cn_date = find_column(['CN_DATE', 'BOOKING_DATE'], df_raw)
        col_days = find_column(['CN_TOTAL_DAYS', 'AGEING', 'DAYS', 'PENDING_DAYS'], df_raw)
        col_reason = find_column(['UNDLVRD_REASON', 'REASON', 'REMARKS', 'DELAY_REASON'], df_raw)
        col_mode = find_column(['MODE', 'SERVICE', 'PRIORITY', 'TRANSIT'], df_raw)
        col_cee = find_column(['CEE', 'CONSIGNEE', 'CLIENT', 'RECEIVER'], df_raw)
        col_pin = find_column(['CEE_PINCODE', 'PINCODE', 'PIN_CODE', 'PIN', 'DEST_PIN'], df_raw)

        df = df_raw.copy()

        # Remove Duplicate CNs (Keeps First Entry)
        if col_cn:
            df = df.drop_duplicates(subset=[col_cn]).copy()

        # Gate-In Date Aging Calculation
        today = pd.to_datetime(datetime.today().date())

        if col_gatein_date:
            gate_in_parsed = pd.to_datetime(df[col_gatein_date], format='%d-%m-%Y', errors='coerce').fillna(
                pd.to_datetime(df[col_gatein_date], dayfirst=True, errors='coerce')
            )
            df['CALCULATED_DAYS'] = (today - gate_in_parsed).dt.days
            
            if col_cn_date:
                cn_parsed = pd.to_datetime(df[col_cn_date], dayfirst=True, errors='coerce')
                df['CALCULATED_DAYS'] = df['CALCULATED_DAYS'].fillna((today - cn_parsed).dt.days)
            if col_days:
                df['CALCULATED_DAYS'] = df['CALCULATED_DAYS'].fillna(pd.to_numeric(df[col_days], errors='coerce'))
                
            df['CALCULATED_DAYS'] = df['CALCULATED_DAYS'].fillna(0).apply(lambda x: max(0, int(x)))
        elif col_cn_date:
            cn_parsed = pd.to_datetime(df[col_cn_date], dayfirst=True, errors='coerce')
            df['CALCULATED_DAYS'] = (today - cn_parsed).dt.days.fillna(0).apply(lambda x: max(0, int(x)))
        elif col_days:
            df['CALCULATED_DAYS'] = pd.to_numeric(df[col_days], errors='coerce').fillna(0).astype(int)
        else:
            df['CALCULATED_DAYS'] = 0

        df['CALCULATED_HOURS'] = df['CALCULATED_DAYS'] * 24

        # Hours Categorization Buckets
        def assign_hour_bucket(hrs):
            if hrs >= 96: return "96 Hour Above"
            elif hrs >= 72: return "72 Hour Above"
            elif hrs >= 48: return "48 Hour Above"
            elif hrs >= 24: return "24 Hour Above"
            else: return "24 Hour Below"

        df['Aging_Bucket'] = df['CALCULATED_HOURS'].apply(assign_hour_bucket)

        # Clean & Calculate CN_PKG & WEIGHT
        if col_pkg:
            df['CN_PKG_NUM'] = pd.to_numeric(df[col_pkg], errors='coerce').fillna(0).astype(int)
        else:
            df['CN_PKG_NUM'] = 0

        if col_wt:
            df['CN_WT_NUM'] = pd.to_numeric(df[col_wt], errors='coerce').fillna(0).round(1)
        else:
            df['CN_WT_NUM'] = 0.0

        # Save to Session State
        st.session_state["processed_df"] = df
        st.session_state["cols"] = {
            "cn": col_cn, "pkg": col_pkg, "wt": col_wt, "todist": col_todist,
            "gatein": col_gatein_date, "cndate": col_cn_date, "reason": col_reason,
            "mode": col_mode, "cee": col_cee, "pin": col_pin
        }

# Render Dashboard if Data exists in Session State
if st.session_state["processed_df"] is not None:
    df_base = st.session_state["processed_df"]
    cols = st.session_state["cols"]

    col_cn, col_pkg, col_wt, col_todist = cols["cn"], cols["pkg"], cols["wt"], cols["todist"]
    col_gatein_date, col_cn_date, col_reason = cols["gatein"], cols["cndate"], cols["reason"]
    col_mode, col_cee, col_pin = cols["mode"], cols["cee"], cols["pin"]

    st.markdown("<br>", unsafe_allow_html=True)

    # Placeholders banाए ताकि KPI कार्ड्स ऊपर दिखें और फिल्टर नीचे आने पर भी KPI अपडेट हो जाएं
    kpi_placeholder = st.container()
    filter_placeholder = st.container()

    # --- STEP 2: MULTI-SELECT FILTER (नीचे प्लेसहोल्डर में) ---
    with filter_placeholder:
        if col_todist:
            all_hubs = sorted(df_base[col_todist].dropna().unique().tolist())
            selected_hubs = st.multiselect(
                "🎯 **Filter Delivery Hubs (TODIST) - Leave blank to view all hubs:**",
                options=all_hubs,
                default=[],
                help="Select specific hubs to filter the entire dashboard data."
            )
            if selected_hubs:
                df = df_base[df_base[col_todist].isin(selected_hubs)].copy()
            else:
                df = df_base.copy()
        else:
            df = df_base.copy()

    # --- STEP 3: TOP KPI METRICS ROW (ऊपर प्लेसहोल्डर में दिखेगा) ---
    with kpi_placeholder:
        total_cn = len(df)
        total_pkg = df['CN_PKG_NUM'].sum()
        total_wt = df['CN_WT_NUM'].sum()
        avg_days = round(df['CALCULATED_DAYS'].mean(), 1) if total_cn > 0 else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        
        c1.metric("Total Unique CNs", f"{total_cn:,}")
        c2.metric("Total CN_PKG (Boxes)", f"{int(total_pkg):,}")
        c3.metric("⚖️ Total Weight Load", format_weight(total_wt) if col_wt else f"{int(total_pkg):,} Pkg")
        c4.metric("🚨 >96 Hours Pendency", f"{len(df[df['Aging_Bucket']=='96 Hour Above']):,}")
        c5.metric("Avg Gate-In Aging", f"{avg_days} Days")

    st.markdown("<br>", unsafe_allow_html=True)

    # SECTION 1: Aging Hours & Undelivered Reasons
    r1_col1, r1_col2 = st.columns(2)

    with r1_col1:
        st.markdown("<div class='section-head'>⏱️ Aging Hours Breakdown (Gate-In)</div>", unsafe_allow_html=True)
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
            font=dict(color='#000000', size=12, family='Inter')
        )
        fig_bucket.update_traces(textfont_size=13, textfont_color='black')
        st.plotly_chart(fig_bucket, use_container_width=True)

    with r1_col2:
        st.markdown("<div class='section-head'>⚠️ Delay Reasons (UNDLVRD_REASON)</div>", unsafe_allow_html=True)
        if col_reason:
            reason_df = df[col_reason].fillna("No Reason Filled").value_counts().head(7).reset_index()
            reason_df.columns = ['Reason', 'Count']

            fig_reason = px.bar(
                reason_df, x='Count', y='Reason', orientation='h', text='Count',
                color='Count', color_continuous_scale='Reds'
            )
            fig_reason.update_layout(
                showlegend=False, height=300, margin=dict(l=0, r=0, t=10, b=0),
                yaxis={'categoryorder': 'total ascending'},
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#000000', size=12, family='Inter')
            )
            fig_reason.update_traces(textfont_size=13, textfont_color='black')
            st.plotly_chart(fig_reason, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # SECTION 2: SIDE-BY-SIDE (MISSING REASONS & TODIST DESTINATION LOAD)
    s2_col1, s2_col2 = st.columns(2)

    with s2_col1:
        st.markdown("<div class='section-head'>📅 Missing UNDLVRD_REASON Tracking</div>", unsafe_allow_html=True)
        gatein_col_to_use = col_gatein_date if col_gatein_date else col_cn_date
        
        if gatein_col_to_use and col_reason:
            df['REASON_STATUS'] = df[col_reason].apply(lambda x: "Missing" if pd.isnull(x) or str(x).strip() == "" or str(x).upper() == "NAN" else "Filled")
            missing_df = df[df['REASON_STATUS'] == "Missing"].copy()
            
            if len(missing_df) > 0:
                missing_df['DATE_OBJ'] = pd.to_datetime(missing_df[gatein_col_to_use], dayfirst=True, errors='coerce')
                missing_df['GATE_IN_DAY'] = missing_df['DATE_OBJ'].dt.strftime('%d-%b-%Y')
                
                tab_m1, tab_m2, tab_m3 = st.tabs(["📅 All Dates", "🎯 Specific Date", "🏢 TODIST Wise"])
                
                # Tab 1: Date Summary
                with tab_m1:
                    missing_summary = missing_df.groupby(['DATE_OBJ', 'GATE_IN_DAY']).agg(
                        Pending_CN_Count=(col_cn if col_cn else col_todist, 'count'),
                        Pending_Packages=('CN_PKG_NUM', 'sum'),
                        Total_Weight=('CN_WT_NUM', 'sum')
                    ).reset_index().sort_values(by='DATE_OBJ', ascending=False)
                    
                    missing_summary['Weight_Formatted'] = missing_summary['Total_Weight'].apply(format_weight)
                    
                    if col_wt:
                        missing_summary_display = missing_summary[['GATE_IN_DAY', 'Pending_CN_Count', 'Pending_Packages', 'Weight_Formatted']]
                        missing_summary_display.columns = ['Gate In Date', 'Blank Reason CNs', 'Pending PKG', 'Weight Load']
                    else:
                        missing_summary_display = missing_summary[['GATE_IN_DAY', 'Pending_CN_Count', 'Pending_Packages']]
                        missing_summary_display.columns = ['Gate In Date', 'Blank Reason CNs', 'Pending PKG']
                        
                    st.dataframe(missing_summary_display, use_container_width=True, hide_index=True, height=225)
                
                # Tab 2: Specific Date + CN List
                with tab_m2:
                    if col_todist:
                        unique_dates = missing_df.sort_values(by='DATE_OBJ', ascending=False)['GATE_IN_DAY'].dropna().unique().tolist()
                        
                        if unique_dates:
                            selected_date = st.radio("🗓️ Click Date to View Details:", options=unique_dates, key="radio_date_picker")
                            filtered_missing = missing_df[missing_df['GATE_IN_DAY'] == selected_date].copy()

                            def join_cns(series):
                                return ", ".join(series.astype(str).unique())

                            todist_missing_summary = filtered_missing.groupby(col_todist).agg(
                                Blank_Reason_CNs=(col_cn if col_cn else col_todist, 'count'),
                                Pending_Packages=('CN_PKG_NUM', 'sum'),
                                Total_Weight=('CN_WT_NUM', 'sum'),
                                Pending_CN_List=(col_cn if col_cn else col_todist, join_cns)
                            ).reset_index().sort_values(by='Blank_Reason_CNs', ascending=False)
                            
                            todist_missing_summary['Weight_Formatted'] = todist_missing_summary['Total_Weight'].apply(format_weight)
                            
                            if col_wt:
                                display_td = todist_missing_summary[[col_todist, 'Blank_Reason_CNs', 'Pending_Packages', 'Weight_Formatted', 'Pending_CN_List']]
                                display_td.columns = ['TODIST Hub', 'Blank Reason CNs', 'Pending PKG', 'Weight Load', 'Pending CN Numbers']
                            else:
                                display_td = todist_missing_summary[[col_todist, 'Blank_Reason_CNs', 'Pending_Packages', 'Pending_CN_List']]
                                display_td.columns = ['TODIST Hub', 'Blank Reason CNs', 'Pending PKG', 'Pending CN Numbers']
                                
                            st.dataframe(display_td, use_container_width=True, hide_index=True, height=160)
                    else:
                        st.info("TODIST column missing in dataset.")

                # Tab 3: TODIST Wise Summary
                with tab_m3:
                    if col_todist:
                        ntc_dest_summary = missing_df.groupby(col_todist).agg(
                            Blank_Reason_CNs=(col_cn if col_cn else col_todist, 'count'),
                            Pending_Packages=('CN_PKG_NUM', 'sum'),
                            Total_Weight=('CN_WT_NUM', 'sum')
                        ).reset_index().sort_values(by='Blank_Reason_CNs', ascending=False)

                        ntc_dest_summary['Weight_Formatted'] = ntc_dest_summary['Total_Weight'].apply(format_weight)

                        if col_wt:
                            display_ntc = ntc_dest_summary[[col_todist, 'Blank_Reason_CNs', 'Pending_Packages', 'Weight_Formatted']]
                            display_ntc.columns = ['TODIST Hub', 'Blank Reason CNs', 'Pending PKG', 'Weight Load']
                        else:
                            display_ntc = ntc_dest_summary[[col_todist, 'Blank_Reason_CNs', 'Pending_Packages']]
                            display_ntc.columns = ['TODIST Hub', 'Blank Reason CNs', 'Pending PKG']

                        st.dataframe(display_ntc, use_container_width=True, hide_index=True, height=225)
                    else:
                        st.info("TODIST column missing in dataset.")
            else:
                st.success("✅ UNDLVRD_REASON is filled for all Gate-In shipments!")
        else:
            st.info("Gate-In Date or UNDLVRD_REASON column not found.")

    with s2_col2:
        st.markdown("<div class='section-head'>🎯 Total TODIST Load Summary</div>", unsafe_allow_html=True)
        if col_todist:
            todist_summary = df.groupby(col_todist).agg(
                Pending_CN_Count=(col_cn if col_cn else col_todist, 'count'),
                Pending_CN_PKG=('CN_PKG_NUM', 'sum'),
                Total_Weight=('CN_WT_NUM', 'sum')
            ).reset_index().sort_values(by='Pending_CN_Count', ascending=False)
            
            todist_summary['Weight_Formatted'] = todist_summary['Total_Weight'].apply(format_weight)
            
            if col_wt:
                display_load = todist_summary[[col_todist, 'Pending_CN_Count', 'Pending_CN_PKG', 'Weight_Formatted']]
                display_load.columns = ['TODIST Hub', 'Pending CN Count', 'Total Pending PKG', 'Total Weight Load']
            else:
                display_load = todist_summary[[col_todist, 'Pending_CN_Count', 'Pending_CN_PKG']]
                display_load.columns = ['TODIST Hub', 'Pending CN Count', 'Total Pending PKG']

            st.dataframe(display_load, use_container_width=True, hide_index=True, height=280)
        else:
            st.info("TODIST column not found in uploaded file.")

    st.markdown("<br>", unsafe_allow_html=True)

    # SECTION 3: CEE_PINCODE & CONSIGNEE ANALYSIS
    r2_col1, r2_col2 = st.columns(2)

    with r2_col1:
        st.markdown("<div class='section-head'>📍 CEE_PINCODE Summary (CN & PKG Count)</div>", unsafe_allow_html=True)
        if col_pin:
            pin_summary = df.groupby(col_pin).agg(
                Pending_CN_Count=(col_cn if col_cn else col_todist, 'count'),
                Pending_CN_PKG=('CN_PKG_NUM', 'sum'),
                Total_Weight=('CN_WT_NUM', 'sum')
            ).reset_index().sort_values(by='Pending_CN_Count', ascending=False)
            
            pin_summary['Weight_Formatted'] = pin_summary['Total_Weight'].apply(format_weight)

            if col_wt:
                display_pin = pin_summary[[col_pin, 'Pending_CN_Count', 'Pending_CN_PKG', 'Weight_Formatted']]
                display_pin.columns = ['Pincode (CEE_PINCODE)', 'Pending CN Count', 'Pending PKG', 'Weight Load']
            else:
                display_pin = pin_summary[[col_pin, 'Pending_CN_Count', 'Pending_CN_PKG']]
                display_pin.columns = ['Pincode (CEE_PINCODE)', 'Pending CN Count', 'Pending PKG']
            
            t_pin1, t_pin2 = st.tabs(["📍 Top Pending Pincodes", "📌 Lowest Pending Pincodes"])
            with t_pin1:
                st.dataframe(display_pin.head(10), use_container_width=True, hide_index=True)
            with t_pin2:
                st.dataframe(display_pin.tail(10), use_container_width=True, hide_index=True)

    with r2_col2:
        st.markdown("<div class='section-head'>🏢 Consignee Analysis (CEE)</div>", unsafe_allow_html=True)
        if col_cee:
            cee_summary = df.groupby(col_cee).agg(
                Pending_CN_Count=(col_cn if col_cn else col_todist, 'count'),
                Pending_CN_PKG=('CN_PKG_NUM', 'sum'),
                Total_Weight=('CN_WT_NUM', 'sum')
            ).reset_index().sort_values(by='Pending_CN_Count', ascending=False)
            
            cee_summary['Weight_Formatted'] = cee_summary['Total_Weight'].apply(format_weight)

            if col_wt:
                display_cee = cee_summary[[col_cee, 'Pending_CN_Count', 'Pending_CN_PKG', 'Weight_Formatted']]
                display_cee.columns = ['Consignee Name (CEE)', 'Pending CN Count', 'Pending PKG', 'Weight Load']
            else:
                display_cee = cee_summary[[col_cee, 'Pending_CN_Count', 'Pending_CN_PKG']]
                display_cee.columns = ['Consignee Name (CEE)', 'Pending CN Count', 'Pending PKG']
            
            t_cee1, t_cee2 = st.tabs(["🔥 Top Pending Clients", "📉 Lowest Pending Clients"])
            with t_cee1:
                st.dataframe(display_cee.head(10), use_container_width=True, hide_index=True)
            with t_cee2:
                st.dataframe(display_cee.tail(10), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Clean Filtered Operations Table
    st.markdown("<div class='section-head'>📋 Clean Unique Operations Dataset</div>", unsafe_allow_html=True)
    show_cols = [c for c in [col_cn, col_todist, col_gatein_date, col_cn_date, col_mode, col_cee, col_pin, col_pkg, col_wt, col_reason] if c]
    
    display_df = df[show_cols + ['CALCULATED_DAYS', 'Aging_Bucket']].sort_values(by='CALCULATED_DAYS', ascending=False)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Export CSV Button
    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Filtered Unique Data (CSV)", data=csv_data, file_name="OmLogistics_Floor_Ops_Unique.csv", mime="text/csv")
