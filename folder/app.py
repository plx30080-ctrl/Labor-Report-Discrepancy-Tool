import streamlit as st
import pandas as pd
from plx_parser import parse_plx
from crescent_parser import parse_crescent
from comparator import merge_and_classify
from summary import generate_summary

st.set_page_config(layout="wide")
st.title("Labor Report Comparison Tool")

# Sidebar controls
st.sidebar.header("Upload Files")
plx_file = st.sidebar.file_uploader("ProLogistix Report", type=["xls", "xlsx"])
crescent_file = st.sidebar.file_uploader("Crescent Report", type=["csv", "xlsx"])

hide_zero_hours = st.sidebar.checkbox("Hide associates with 0 hours (PLX)", value=True)
show_all = st.sidebar.toggle("Show all rows (including matches)", value=False)

if plx_file and crescent_file:
    # Parse
    plx_df = parse_plx(plx_file)
    if hide_zero_hours:
        before = len(plx_df)
        plx_df = plx_df[plx_df["Total_Hours"] > 0]
        st.sidebar.info(f"Filtered out {before - len(plx_df)} associates with 0 hours")

    crescent_df = parse_crescent(crescent_file)

    # Merge and classify
    merged = merge_and_classify(plx_df, crescent_df, hour_tolerance=0.01)

    # Toggle behavior: only discrepancies by default
    display_df = merged if show_all else merged[merged["Discrepancy"] != "Match"].reset_index(drop=True)

    # Discrepancy review
    st.subheader("Discrepancy Review")
    edited_df = st.data_editor(
        display_df,
        num_rows="dynamic",
        width="stretch",
    key="discrepancy_editor"
)    

    # Allow user to select rows to merge
    selected_rows = st.multiselect(
        "Select rows to merge (by index)",
        options=edited_df.index.tolist()
)

    if st.button("Merge Selected"):
        if len(selected_rows) > 1:
            # Take the first row as base
            base = edited_df.loc[selected_rows[0]].copy()
            # Sum hours across selected rows
            base["Total_Hours_PLX"] = edited_df.loc[selected_rows, "Total_Hours_PLX"].sum(min_count=1)
            base["Total_Hours_Crescent"] = edited_df.loc[selected_rows, "Total_Hours_Crescent"].sum(min_count=1)
            # Combine notes/resolution
            base["Notes"] = "; ".join(edited_df.loc[selected_rows, "Notes"].astype(str))
            base["Resolution"] = "Merged manually"
            # Drop old rows and append merged
            edited_df = edited_df.drop(selected_rows).append(base, ignore_index=True)
            st.success("Rows merged successfully. Scroll down to see updated table.")

    # Totals: only valid EIDs included already
    plx_total = plx_df["Total_Hours"].sum()
    crescent_total = crescent_df["Total_Hours"].sum()

    c1, c2 = st.columns(2)
    c1.metric("PLX Total Hours", f"{plx_total:.2f}")
    c2.metric("Crescent Total Hours", f"{crescent_total:.2f}")

    diff = plx_total - crescent_total
    if abs(diff) < 0.01:
        st.success("✅ Totals match")
    else:
        st.warning(f"⚠️ Difference of {diff:.2f} hours")

    # Client summary
    st.subheader("Client Summary")
    summary_text = generate_summary(edited_df)
    st.text_area("Email Summary", summary_text, height=300)
else:
    st.info("Please upload both PLX and Crescent reports.")
