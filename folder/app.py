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
        st.sidebar
