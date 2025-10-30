import streamlit as st
import pandas as pd
from plx_parser import parse_plx
from crescent_parser import parse_crescent

st.set_page_config(layout="wide")
st.title("Labor Report Comparison Tool")

# Initialize session state for edited data
if "plx_df" not in st.session_state:
    st.session_state["plx_df"] = None
if "crescent_df" not in st.session_state:
    st.session_state["crescent_df"] = None

# Sidebar controls
st.sidebar.header("Upload Files")
plx_file = st.sidebar.file_uploader("ProLogistix Report", type=["xls", "xlsx"])
crescent_file = st.sidebar.file_uploader("Crescent Report", type=["csv", "xlsx"])
hide_zero_hours = st.sidebar.checkbox("Hide associates with 0 hours (PLX)", value=True)

def recalc_tables():
    """Recalculate comparison and unreconciled tables from session state."""
    plx_df = st.session_state["plx_df"]
    crescent_df = st.session_state["crescent_df"]

    # Apply zero-hour filter
    if hide_zero_hours and plx_df is not None:
        plx_df = plx_df[plx_df["Total_Hours"] > 0]

    # Crescent view
    crescent_view = crescent_df[["EID", "Badge", "Lines", "Total_Hours"]].copy()
    crescent_view["Badge_Last3"] = crescent_view["Badge"].astype(str).str[-3:]
    crescent_view = crescent_view[["EID", "Badge_Last3", "Lines", "Total_Hours"]]

    # PLX view
    plx_view = plx_df[["EID", "Name", "Total_Hours"]].copy()

    # Comparison
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

    # Unreconciled
    unreconciled = comparison[
        (comparison["Status"] == "Mismatch")
        | (comparison["Total_Hours_PLX"].isna())
        | (comparison["Total_Hours_Crescent"].isna())
    ].copy()

    return crescent_view, plx_view, comparison, unreconciled

if plx_file and crescent_file:
    # Parse and store in session state if not already
    if st.session_state["plx_df"] is None or st.session_state["crescent_df"] is None:
        st.session_state["plx_df"] = parse_plx(plx_file)
        st.session_state["crescent_df"] = parse_crescent(crescent_file)

    crescent_view, plx_view, comparison, unreconciled = recalc_tables()

    # Layout: 3 columns for tables 1–3
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Table 1: Crescent Detail")
        edited_crescent = st.data_editor(
            crescent_view,
            num_rows="dynamic",
            width="stretch",
            key="crescent_editor"
        )

    with col2:
        st.markdown("### Table 2: PLX Detail")
        edited_plx = st.data_editor(
            plx_view,
            num_rows="dynamic",
            width="stretch",
            key="plx_editor"
        )

    with col3:
        st.markdown("### Table 3: Comparison Summary")
        edited_comparison = st.data_editor(
            comparison[["EID", "Name", "Total_Hours_Crescent", "Total_Hours_PLX", "Status"]],
            num_rows="dynamic",
            width="stretch",
            key="comparison_editor"
        )

    if st.button("Save & Refresh Tables"):
        # Update session state with edits
        st.session_state["crescent_df"].update(edited_crescent.set_index("EID"))
        st.session_state["plx_df"].update(edited_plx.set_index("EID"))

        # If hours were edited in comparison, push back to source
        for _, row in edited_comparison.iterrows():
            eid = str(row["EID"])
            if eid in st.session_state["crescent_df"]["EID"].astype(str).values:
                st.session_state["crescent_df"].loc[
                    st.session_state["crescent_df"]["EID"].astype(str) == eid, "Total_Hours"
                ] = row["Total_Hours_Crescent"]
            if eid in st.session_state["plx_df"]["EID"].astype(str).values:
                st.session_state["plx_df"].loc[
                    st.session_state["plx_df"]["EID"].astype(str) == eid, "Total_Hours"
                ] = row["Total_Hours_PLX"]

        st.success("Edits saved and tables refreshed.")
        crescent_view, plx_view, comparison, unreconciled = recalc_tables()

    # Table 4: Unreconciled Issues
    st.subheader("Table 4: Unreconciled Issues")
    edited_unreconciled = st.data_editor(
        unreconciled,
        num_rows="dynamic",
        width="stretch",
        key="unreconciled_editor"
    )

    if st.button("Save & Refresh Unreconciled"):
        # Apply edits back into source data
        for _, row in edited_unreconciled.iterrows():
            eid = str(row["EID"])
            if pd.notna(row.get("Total_Hours_Crescent")):
                st.session_state["crescent_df"].loc[
                    st.session_state["crescent_df"]["EID"].astype(str) == eid, "Total_Hours"
                ] = row["Total_Hours_Crescent"]
            if pd.notna(row.get("Total_Hours_PLX")):
                st.session_state["plx_df"].loc[
                    st.session_state["plx_df"]["EID"].astype(str) == eid, "Total_Hours"
                ] = row["Total_Hours_PLX"]
        st.success("Unreconciled edits saved and tables refreshed.")
        crescent_view, plx_view, comparison, unreconciled = recalc_tables()

    # Totals
    plx_total = st.session_state["plx_df"]["Total_Hours"].sum()
    crescent_total = st.session_state["crescent_df"]["Total_Hours"].sum()
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
