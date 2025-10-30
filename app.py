import streamlit as st
import pandas as pd
from plx_parser import parse_plx
from crescent_parser import parse_crescent
from comparator import compare_reports
from summary import generate_summary

st.set_page_config(layout="wide")
st.title("Labor Report Comparison Tool")

# Sidebar
st.sidebar.header("Upload Files")
plx_file = st.sidebar.file_uploader("ProLogistix Report", type=["xls", "xlsx"])
crescent_file = st.sidebar.file_uploader("Crescent Report", type=["csv", "xlsx"])
day_filter = st.sidebar.selectbox("Filter by Day", ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])

if plx_file and crescent_file:
    plx_df = parse_plx(plx_file)
    crescent_df = parse_crescent(crescent_file)
    
    merged_df = compare_reports(plx_df, crescent_df)
    st.subheader("Discrepancy Review")
    edited_df = st.data_editor(merged_df, num_rows="dynamic", width="stretch")

    # Totals
    plx_total = plx_df["Total_Hours"].sum()
    crescent_total = crescent_df["Total_Hours"].sum()
    st.metric("PLX Total Hours", f"{plx_total:.2f}")
    st.metric("Crescent Total Hours", f"{crescent_total:.2f}")

    if abs(plx_total - crescent_total) < 0.01:
        st.success("✅ Totals match")
    else:
        st.warning(f"⚠️ Difference of {plx_total - crescent_total:.2f} hours")

    # Summary
    st.subheader("Client Summary")
    summary_text = generate_summary(edited_df)
    st.text_area("Email Summary", summary_text, height=300)
