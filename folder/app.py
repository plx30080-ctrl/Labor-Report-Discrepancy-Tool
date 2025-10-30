import streamlit as st
import pandas as pd
from plx_parser import parse_plx
from crescent_parser import parse_crescent

st.set_page_config(layout="wide")
st.title("Labor Report Comparison Tool")

# Sidebar controls
st.sidebar.header("Upload Files")
plx_file = st.sidebar.file_uploader("ProLogistix Report", type=["xls", "xlsx"])
crescent_file = st.sidebar.file_uploader("Crescent Report", type=["csv", "xlsx"])

hide_zero_hours = st.sidebar.checkbox("Hide associates with 0 hours (PLX)", value=True)

if plx_file and crescent_file:
    # Parse raw sources
    plx_df = parse_plx(plx_file)
    crescent_df = parse_crescent(crescent_file)

    # Apply zero-hour filter (PLX)
    if hide_zero_hours:
        before = len(plx_df)
        plx_df = plx_df[plx_df["Total_Hours"] > 0]
        st.sidebar.info(f"Filtered out {before - len(plx_df)} associates with 0 hours")

    # --- Table 1: Crescent detail ---
    crescent_view = crescent_df[["EID", "Badge", "Lines", "Total_Hours"]].copy()
    crescent_view["Badge_Last3"] = crescent_view["Badge"].astype(str).str[-3:]
    crescent_view = crescent_view[["EID", "Badge_Last3", "Lines", "Total_Hours"]]

    st.markdown("### Table 1: Crescent Detail")
    st.dataframe(crescent_view, use_container_width=True)

    # --- Table 2: PLX detail ---
    plx_view = plx_df[["EID", "Name", "Total_Hours"]].copy()

    st.markdown("### Table 2: PLX Detail")
    st.dataframe(plx_view, use_container_width=True)

    # --- Table 3: Comparison summary ---
    comparison = pd.merge(
        plx_view, crescent_view,
        on="EID", how="outer", suffixes=("_PLX", "_Crescent")
    )

    comparison["Status"] = comparison.apply(
        lambda r: "Match"
        if pd.notna(r["Total_Hours_PLX"])
        and pd.notna(r["Total_Hours_Crescent"])
        and abs(r["Total_Hours_PLX"] - r["Total_Hours_Crescent"]) < 0.01
        else "Mismatch",
        axis=1,
    )

    st.markdown("### Table 3: Comparison Summary")
    st.dataframe(
        comparison[["EID", "Name", "Total_Hours_Crescent", "Total_Hours_PLX", "Status"]],
        use_container_width=True,
    )

    # --- Table 4: Unreconciled Issues ---
    st.subheader("Unreconciled Issues")

    unreconciled = comparison[
        (comparison["Status"] == "Mismatch")
        | (comparison["Total_Hours_PLX"].isna())
        | (comparison["Total_Hours_Crescent"].isna())
    ].copy()

    edited_unreconciled = st.data_editor(
        unreconciled,
        num_rows="dynamic",
        width="stretch",
        key="unreconciled_editor",
    )

    if st.button("Save & Refresh"):
        # Replace the unreconciled rows with edited ones
        st.session_state["manual_fixes"] = edited_unreconciled
        st.success("Edits saved. Please rerun to refresh the discrepancy tables.")

    # Totals
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

else:
    st.info("Please upload both PLX and Crescent reports.")
