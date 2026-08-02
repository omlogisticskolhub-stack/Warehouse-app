from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Page Configuration - Clean Dashboard
st.set_page_config(page_title="Floor Ops Dashboard - Om Logistics", layout="wide")

# ==========================================
# 🔒 SIMPLE PASSWORD AUTHENTICATION SYSTEM
# ==========================================
# Fixed Password
DASHBOARD_PASSWORD = st.secrets.get("DASHBOARD_PASSWORD", "Dhiraj@01072026")


def check_password():
    """Returns `True` if the user enters the correct password."""

    def password_entered():
        if st.session_state["entered_password"] == DASHBOARD_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["entered_password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🚛 Floor Ops Analytics - Om Logistics")
            st.text_input(
                "🔒 Enter Dashboard Password to Access:",
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
                "🔒 Enter Dashboard Password to Access:",
                type="password",
                on_change=password_entered,
                key="entered_password",
            )
            st.error("❌ Incorrect Password! Please try again.")
        return False
    else:
        return True


if not check_password():
    st.stop()

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

with st.sidebar:
    st.markdown("### 🔑 Account Actions")
    if st.button("🔒 Lock Dashboard / Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

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

        df["Aging_Bucket"] = df["CALCULATED_HOURS"].apply(assign_hour_bucket)

        if col_pkg:
            df["CN_PKG_NUM"] = (
                pd.to_numeric(df[col_pkg], errors="coerce")
                .fillna(0)
                .astype(int)
            )
        else:
            df["CN_PKG_NUM"] = 0

        if col_wt:
            df["CN_WT_NUM"] = (
                pd.to_numeric(df[col_wt], errors="coerce").fillna(0).round(1)
            )
        else:
            df["CN_WT_NUM"] = 0.0

        if col_reason:
            df["REASON_CLEAN"] = df[col_reason].apply(
                lambda x: "Pending Reason"
                if pd.isnull(x) or str(x).strip() in ["", "-", "NAN", "NONE"]
                else str(x).strip()
            )
            df["REASON_STATUS"] = df["REASON_CLEAN"].apply(
                lambda x: "Missing" if x == "Pending Reason" else "Filled"
            )

        st.session_state["processed_df"] = df
        st.session_state["cols"] = {
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

if st.session_state["processed_df"] is not None:
    df_raw_loaded = st.session_state["processed_df"]
    cols = st.session_state["cols"]

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
    col_mode, col_cee, col_pin = cols["mode"], cols["cee"], cols["pin"]

    st.markdown("<br>", unsafe_allow_html=True)

    all_hubs = (
        sorted(df_raw_loaded[col_todist].dropna().unique().tolist())
        if col_todist
        else []
    )
    unique_dates_df = df_raw_loaded.dropna(subset=["DATE_OBJ"]).sort_values(
        by="DATE_OBJ", ascending=False
    )
    all_dates = unique_dates_df["GATE_IN_DAY"].unique().tolist()

    all_specific_reasons = (
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

    kpi_container = st.container()
    filter_container = st.container()

    # =========================================================
    # STEP 3: MASTER FILTERS
    # =========================================================
    with filter_container:
        st.markdown("<br>", unsafe_allow_html=True)
        f_col1, f_col2, f_col3, f_col4 = st.columns([1, 1, 1, 1])

        with f_col1:
            selected_hubs = st.multiselect(
                "🏢 **TODIST Hub Filter:**",
                options=all_hubs,
                default=[],
                help="Select TODIST hubs.",
            )

        with f_col2:
            select_all_dates = st.checkbox(
                "✅ **Select All Dates**", value=True
            )
            default_date_selection = all_dates if select_all_dates else []

            selected_dates = st.multiselect(
                "🗓️ **Select Dates:**",
                options=all_dates,
                default=default_date_selection,
            )

        with f_col3:
            reason_filter = st.selectbox(
                "⚡ **Reason Status Filter:**",
                options=[
                    "All Status",
                    "Pending Reason Only",
                    "Updated Reason Only",
                ],
                index=0,
            )

        with f_col4:
            selected_specific_reasons = st.multiselect(
                "⚠️ **Specific Reason Filter:**",
                options=all_specific_reasons,
                default=[],
                help="Select specific updated delay reasons.",
            )

    # =========================================================
    # ⚡ MASTER DYNAMIC FILTERING LOGIC
    # =========================================================
    df_filtered = df_raw_loaded.copy()

    if selected_hubs:
        df_filtered = df_filtered[
            df_filtered[col_todist].isin(selected_hubs)
        ].copy()

    if selected_dates:
        df_filtered = df_filtered[
            df_filtered["GATE_IN_DAY"].isin(selected_dates)
        ].copy()
    else:
        df_filtered = df_filtered.iloc[0:0]

    if reason_filter == "Pending Reason Only":
        df_filtered = df_filtered[
            df_filtered["REASON_STATUS"] == "Missing"
        ].copy()
    elif reason_filter == "Updated Reason Only":
        df_filtered = df_filtered[
            df_filtered["REASON_STATUS"] == "Filled"
        ].copy()

    if selected_specific_reasons:
        df_filtered = df_filtered[
            df_filtered["REASON_CLEAN"].isin(selected_specific_reasons)
        ].copy()

    df = df_filtered.copy()

    # =========================================================
    # STEP 2: TOP KPI CARDS
    # =========================================================
    total_cn = len(df)
    total_pkg = df["CN_PKG_NUM"].sum() if total_cn > 0 else 0
    total_wt = df["CN_WT_NUM"].sum() if total_cn > 0 else 0
    avg_days = round(df["CALCULATED_DAYS"].mean(), 1) if total_cn > 0 else 0

    pending_reason_count = (
        len(df[df["REASON_STATUS"] == "Missing"]) if col_reason else 0
    )
    updated_reason_count = (
        len(df[df["REASON_STATUS"] == "Filled"]) if col_reason else 0
    )

    with kpi_container:
        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        c1.metric("Total Unique CNs", f"{total_cn:,}")
        c2.metric("Total PKG", f"{int(total_pkg):,}")
        c3.metric(
            "⚖️ Weight Load",
            format_weight(total_wt) if col_wt else f"{int(total_pkg):,} Pkg",
        )
        c4.metric(
            "🚨 >96 Hours",
            f"{len(df[df['Aging_Bucket']=='96 Hour Above']):,}",
        )
        c5.metric("Avg Aging", f"{avg_days} Days")
        c6.metric("Pending Reason", f"{pending_reason_count:,}")
        c7.metric("Reason Updated", f"{updated_reason_count:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # SECTION 1: Aging Hours & Undelivered Reasons
    r1_col1, r1_col2 = st.columns(2)

    with r1_col1:
        st.markdown(
            "<div class='section-head'>⏱️ Aging Hours Breakdown"
            " (Gate-In)</div>",
            unsafe_allow_html=True,
        )
        bucket_order = [
            "96 Hour Above",
            "72 Hour Above",
            "48 Hour Above",
            "24 Hour Above",
            "24 Hour Below",
        ]
        bucket_df = (
            df["Aging_Bucket"]
            .value_counts()
            .reindex(bucket_order)
            .fillna(0)
            .reset_index()
        )
        bucket_df.columns = ["Hour Bucket", "Shipment Count"]

        fig_bucket = px.bar(
            bucket_df,
            x="Hour Bucket",
            y="Shipment Count",
            text="Shipment Count",
            color="Hour Bucket",
            color_discrete_map={
                "96 Hour Above": "#b91c1c",
                "72 Hour Above": "#ef4444",
                "48 Hour Above": "#f97316",
                "24 Hour Above": "#eab308",
                "24 Hour Below": "#22c55e",
            },
        )
        fig_bucket.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#000000", size=12, family="Inter"),
        )
        fig_bucket.update_traces(textfont_size=13, textfont_color="black")
        st.plotly_chart(fig_bucket, use_container_width=True)

    with r1_col2:
        st.markdown(
            "<div class='section-head'>⚠️ Delay Reasons Breakdown</div>",
            unsafe_allow_html=True,
        )
        if col_reason:
            reason_df = (
                df[df["REASON_STATUS"] == "Filled"]["REASON_CLEAN"]
                .value_counts()
                .head(7)
                .reset_index()
            )
            reason_df.columns = ["Reason", "Count"]

            if len(reason_df) > 0:
                fig_reason = px.bar(
                    reason_df,
                    x="Count",
                    y="Reason",
                    orientation="h",
                    text="Count",
                    color="Count",
                    color_continuous_scale="Reds",
                )
                fig_reason.update_layout(
                    showlegend=False,
                    height=300,
                    margin=dict(l=0, r=0, t=10, b=0),
                    yaxis={"categoryorder": "total ascending"},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#000000", size=12, family="Inter"),
                )
                fig_reason.update_traces(
                    textfont_size=13, textfont_color="black"
                )
                st.plotly_chart(fig_reason, use_container_width=True)
            else:
                st.info(
                    "No updated delay reasons found for current selection."
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # SECTION 2: MISSING REASONS & TODIST DESTINATION LOAD
    s2_col1, s2_col2 = st.columns(2)

    with s2_col1:
        st.markdown(
            "<div class='section-head'>📅 Missing UNDLVRD_REASON Tracking</div>",
            unsafe_allow_html=True,
        )

        if col_reason:
            missing_df = df[df["REASON_STATUS"] == "Missing"].copy()

            if len(missing_df) > 0:
                tab_m1, tab_m2 = st.tabs(
                    ["📅 Dates Breakdown", "🏢 TODIST Wise Details"]
                )

                with tab_m1:
                    missing_summary = (
                        missing_df.groupby(["DATE_OBJ", "GATE_IN_DAY"])
                        .agg(
                            Pending_CN_Count=(
                                col_cn if col_cn else col_todist,
                                "count",
                            ),
                            Pending_Packages=("CN_PKG_NUM", "sum"),
                            Total_Weight=("CN_WT_NUM", "sum"),
                        )
                        .reset_index()
                        .sort_values(by="DATE_OBJ", ascending=False)
                    )

                    missing_summary["Weight_Formatted"] = missing_summary[
                        "Total_Weight"
                    ].apply(format_weight)

                    if col_wt:
                        missing_summary_display = missing_summary[
                            [
                                "GATE_IN_DAY",
                                "Pending_CN_Count",
                                "Pending_Packages",
                                "Weight_Formatted",
                            ]
                        ]
                        missing_summary_display.columns = [
                            "Gate In Date",
                            "Blank Reason CNs",
                            "Pending PKG",
                            "Weight Load",
                        ]
                    else:
                        missing_summary_display = missing_summary[
                            [
                                "GATE_IN_DAY",
                                "Pending_CN_Count",
                                "Pending_Packages",
                            ]
                        ]
                        missing_summary_display.columns = [
                            "Gate In Date",
                            "Blank Reason CNs",
                            "Pending PKG",
                        ]

                    st.dataframe(
                        missing_summary_display,
                        use_container_width=True,
                        hide_index=True,
                        height=250,
                    )

                with tab_m2:
                    if col_todist:

                        def join_cns(series):
                            return ", ".join(series.astype(str).unique())

                        todist_missing_summary = (
                            missing_df.groupby(col_todist)
                            .agg(
                                Blank_Reason_CNs=(
                                    col_cn if col_cn else col_todist,
                                    "count",
                                ),
                                Pending_Packages=("CN_PKG_NUM", "sum"),
                                Total_Weight=("CN_WT_NUM", "sum"),
                                Pending_CN_List=(
                                    col_cn if col_cn else col_todist,
                                    join_cns,
                                ),
                            )
                            .reset_index()
                            .sort_values(
                                by="Blank_Reason_CNs", ascending=False
                            )
                        )

                        todist_missing_summary["Weight_Formatted"] = (
                            todist_missing_summary["Total_Weight"].apply(
                                format_weight
                            )
                        )

                        if col_wt:
                            display_td = todist_missing_summary[
                                [
                                    col_todist,
                                    "Blank_Reason_CNs",
                                    "Pending_Packages",
                                    "Weight_Formatted",
                                    "Pending_CN_List",
                                ]
                            ]
                            display_td.columns = [
                                "TODIST Hub",
                                "Blank Reason CNs",
                                "Pending PKG",
                                "Weight Load",
                                "Pending CN Numbers",
                            ]
                        else:
                            display_td = todist_missing_summary[
                                [
                                    col_todist,
                                    "Blank_Reason_CNs",
                                    "Pending_Packages",
                                    "Pending_CN_List",
                                ]
                            ]
                            display_td.columns = [
                                "TODIST Hub",
                                "Blank Reason CNs",
                                "Pending PKG",
                                "Pending CN Numbers",
                            ]

                        st.dataframe(
                            display_td,
                            use_container_width=True,
                            hide_index=True,
                            height=250,
                        )
                    else:
                        st.info("TODIST column missing in dataset.")
            else:
                st.success(
                    "✅ UNDLVRD_REASON is filled for all selected Filtered"
                    " shipments!"
                )
        else:
            st.info("UNDLVRD_REASON column not found.")

    with s2_col2:
        st.markdown(
            "<div class='section-head'>🎯 Total TODIST Load Summary</div>",
            unsafe_allow_html=True,
        )
        if col_todist:
            todist_summary = (
                df.groupby(col_todist)
                .agg(
                    Pending_CN_Count=(col_cn if col_cn else col_todist, "count"),
                    Pending_CN_PKG=("CN_PKG_NUM", "sum"),
                    Total_Weight=("CN_WT_NUM", "sum"),
                )
                .reset_index()
                .sort_values(by="Pending_CN_Count", ascending=False)
            )

            todist_summary["Weight_Formatted"] = todist_summary[
                "Total_Weight"
            ].apply(format_weight)

            if col_wt:
                display_load = todist_summary[
                    [
                        col_todist,
                        "Pending_CN_Count",
                        "Pending_CN_PKG",
                        "Weight_Formatted",
                    ]
                ]
                display_load.columns = [
                    "TODIST Hub",
                    "Pending CN Count",
                    "Total Pending PKG",
                    "Total Weight Load",
                ]
            else:
                display_load = todist_summary[
                    [col_todist, "Pending_CN_Count", "Pending_CN_PKG"]
                ]
                display_load.columns = [
                    "TODIST Hub",
                    "Pending CN Count",
                    "Total Pending PKG",
                ]

            st.dataframe(
                display_load,
                use_container_width=True,
                hide_index=True,
                height=280,
            )
        else:
            st.info("TODIST column not found in uploaded file.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Clean Filtered Operations Table
    st.markdown(
        "<div class='section-head'>📋 Clean Unique Operations Dataset"
        " (Filtered)</div>",
        unsafe_allow_html=True,
    )
    show_cols = [
        c
        for c in [
            col_cn,
            col_todist,
            col_gatein_date,
            col_cn_date,
            col_mode,
            col_cee,
            col_pin,
            col_pkg,
            col_wt,
            col_reason,
        ]
        if c
    ]

    display_df = df[show_cols + ["CALCULATED_DAYS", "Aging_Bucket"]].sort_values(
        by="CALCULATED_DAYS", ascending=False
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Export CSV Button
    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Filtered Unique Data (CSV)",
        data=csv_data,
        file_name="OmLogistics_Floor_Ops_Filtered.csv",
        mime="text/csv",
    )
