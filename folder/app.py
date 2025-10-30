import streamlit as st
import pandas as pd
from plx_parser import parse_plx
from crescent_parser import parse_crescent
from comparator import compare_reports
from summary import generate_summary

# Streamlit page setup
st.set_page_config(layout="wide")
st.title("Labor Report Comparison Tool")

# Sidebar controls
st.sidebar.header("Upload Files")
plx_file = st.sidebar.file_uploader("ProLogistix Report", type=["xls", "xlsx"])
crescent_file = st.sidebar.file_uploader("Crescent Report", type=["csv", "xlsx"])

# New filter toggle
hide_zero_hours = st.sidebar.checkbox("Hide associates with 0 hours (PLX)", value=True)

day_filter = st.sidebar.selectbox(
    "Filter by Day",
    ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
)

# Main workflow
if plx_file and crescent_file:
    # Parse PLX
    plx_df = parse_plx(plx_file)

    # Apply zero-hour filter
    if hide_zero_hours:
        before_count = len(plx_df)
        plx_df = plx_df[plx_df["Total_Hours"] > 0]
        after_count = len(plx_df)
        st.sidebar.info(f"Filtered out {before_count - after_count} associates with 0 hours")

    # Parse Crescent
    crescent_df = parse_crescent(crescent_file)

    # Compare reports
    merged_df = compare_reports(plx_df, crescent_df)

    # Editable discrepancy review
    st.subheader("Discrepancy Review")
    edited_df = st.data_editor(
        merged_df,
        num_rows="dynamic",
        width="stretch"
    )

    # Totals
    plx_total = plx_df["Total_Hours"].sum()
    crescent_total = crescent_df["Total_Hours"].sum()

    col1, col2 = st.columns(2)
    col1.metric("PLX Total Hours", f"{plx_total:.2f}")
    col2.metric("Crescent Total Hours", f"{crescent_total:.2f}")

    if abs(plx_total - crescent_total) < 0.01:
        st.success("✅ Totals match")
    else:
        st.warning(f"⚠️ Difference of {plx_total - crescent_total:.2f} hours")

    # Client summary
    st.subheader("Client Summary")
    summary_text = generate_summary(edited_df)
    st.text_area("Email Summary", summary_text, height=300)
