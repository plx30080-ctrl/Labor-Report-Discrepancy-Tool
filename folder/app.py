import streamlit as st
import pandas as pd
from plx_parser import parse_plx
from crescent_parser import parse_crescent

st.set_page_config(layout="wide")
st.title("Labor Report Comparison Tool")

# Initialize session state
if "plx_df" not in st.session_state:
    st.session_state["plx_df"] = None
if "crescent_df" not in st.session_state:
    st.session_state["crescent_df"] = None

# Sidebar
st.sidebar.header("Upload Files")
plx_file = st.sidebar.file_uploader("ProLogistix Report", type=["xls", "xlsx"])
crescent_file = st.sidebar.file_uploader("Crescent Report", type=["csv", "xlsx"])
hide_zero_hours = st.sidebar.checkbox("Hide associates with 0 hours (PLX)", value=True)

def recalc_tables():
    plx_df = st.session_state["plx_df"].copy()
    crescent_df = st.session_state["crescent_df"].copy()

    if hide_zero_hours:
        plx_df = plx_df[plx_df["Total_Hours"] > 0]

    crescent_view = crescent_df[["EID", "Badge", "Lines", "Total_Hours"]].copy()
    crescent_view["Badge_Last3"] = crescent_view["Badge"].astype(str).str[-3:]
    crescent_view = crescent_view[["EID", "Badge_Last3", "Lines", "Total_Hours"]]

    plx_view = plx_df[["EID", "Name", "Total_Hours"]].copy()

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
    return crescent_view, plx_view, comparison

if plx_file and crescent_file:
    if st.session_state["plx_df"] is None or st.session_state["crescent_df"] is None:
        st.session_state["plx_df"] = parse_plx(plx_file)
        st.session_state["crescent_df"] = parse_crescent(crescent_file)

    crescent_view, plx_view, comparison = recalc_tables()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Table 1: Crescent Detail")
        edited_crescent = st.data_editor(crescent_view, key="crescent_editor", use_container_width=True)
        # Push edits back
        st.session_state["crescent_df"].update(edited_crescent.set_index("EID"))

    with col2:
        st.markdown("### Table 2: PLX Detail")
        edited_plx = st.data_editor(plx_view, key="plx_editor", use_container_width=True)
        st.session_state["plx_df"].update(edited_plx.set_index("EID"))

    with col3:
        st.markdown("### Table 3: Comparison Summary")
        edited_comp = st.data_editor(
            comparison[["EID", "Name", "Total_Hours_Crescent", "Total_Hours_PLX", "Status"]],
            key="comparison_editor",
            use_container_width=True
        )
                # --- Table 4: Mismatches Only ---
        st.markdown("### Table 4: Mismatched Items Only")
        mismatches = comparison[comparison["Status"] == "Mismatch"].copy()
        st.dataframe(
        mismatches[["EID", "Name", "Total_Hours_Crescent", "Total_Hours_PLX", "Status"]],
        use_container_width=False
        )

    
        # Push hour edits back to sources
        for _, row in edited_comp.iterrows():
            eid = str(row["EID"])
            if pd.notna(row["Total_Hours_Crescent"]):
                st.session_state["crescent_df"].loc[
                    st.session_state["crescent_df"]["EID"].astype(str) == eid, "Total_Hours"
                ] = row["Total_Hours_Crescent"]
            if pd.notna(row["Total_Hours_PLX"]):
                st.session_state["plx_df"].loc[
                    st.session_state["plx_df"]["EID"].astype(str) == eid, "Total_Hours"
                ] = row["Total_Hours_PLX"]

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
