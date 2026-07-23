import streamlit as st
import pandas as pd

st.set_page_config(page_title="Warehouse Stock & Aging Dashboard", layout="wide")

st.title("📦 Warehouse Stock & Aging Live Dashboard")
st.write("Upload your daily warehouse Excel file below to generate real-time analytics and download reports.")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    with st.spinner("Processing file and generating analytics..."):
        df = pd.read_excel(uploaded_file)
        
        # Key Metrics Calculation
        total_cases = len(df)
        avg_aging = round(df['CN_TOTAL_DAYS'].mean(), 1)
        max_aging = df['CN_TOTAL_DAYS'].max()
        over_90 = len(df[df['CN_TOTAL_DAYS'] > 90])
        days_30_90 = len(df[(df['CN_TOTAL_DAYS'] > 30) & (df['CN_TOTAL_DAYS'] <= 90)])
        missing_remarks_cases = len(df[(df['CN_REMARKS'].isna() | (df['CN_REMARKS'].astype(str).str.strip().isin(['', 'nan']))) & 
                                       (df['UNDLVRD_REASON'].isna() | (df['UNDLVRD_REASON'].astype(str).str.strip().isin(['', 'nan'])))])
        
        # KPI Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Cases", f"{total_cases:,}")
        col2.metric("> 90 Days Old", f"{over_90}")
        col3.metric("31-90 Days Old", f"{days_30_90}")
        col4.metric("Avg Aging", f"{avg_aging} Days")
        col5.metric("Blank Remarks", f"{missing_remarks_cases}")
        
        st.divider()
        
        # Top 10 Oldest Cases Table
        st.subheader("🚨 Top 10 Oldest Pending Cases")
        top10_df = df.sort_values(by='CN_TOTAL_DAYS', ascending=False).head(10)
        st.dataframe(top10_df[['CN_CN_NO', 'CEE', 'FROMSOURCE', 'CN_DATE', 'CN_TOTAL_DAYS', 'UNDLVRD_REASON', 'CN_REMARKS']])
        
        # Download Old Cases Button
        st.divider()
        st.subheader("📥 Export Critical Old Cases")
        old_cases = df[df['CN_TOTAL_DAYS'] > 30].sort_values(by='CN_TOTAL_DAYS', ascending=False)
        csv = old_cases.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Old Cases (>30 Days) as CSV",
            data=csv,
            file_name='old_warehouse_cases.csv',
            mime='text/csv',
        )
