import streamlit as st
import pandas as pd
from plx_parser import parse_plx
from crescent_parser import parse_crescent
from comparator import merge_and_classify
from summary import generate_summary

st.set_page_config(layout="wide")
st.title("Labor Report Comparison Tool")

# Initialize session state for EID alias map
if "eid_aliases" not in st.session_state:
    st.session_state["eid_aliases"] = {}  # {old_eid: canonical_eid}

# Sidebar controls
st.sidebar.header("Upload Files")
plx_file = st.sidebar.file_uploader("ProLogistix Report", type=["xls", "xlsx"])
crescent_file = st.sidebar.file_uploader("Crescent Report", type=["csv", "xlsx"])

hide_zero_hours = st.sidebar.checkbox("Hide associates with 0 hours (PLX)", value=True)
show_all = st.sidebar.toggle("Show all rows (including matches)", value=False)

def apply_aliases(df, eid_col="EID"):
    """Map EIDs to canonical ones using session alias map."""
    aliases = st.session_state["eid_aliases"]
    if not aliases:
        return df
    mapped = df.copy()
    mapped[eid_col] = mapped[eid_col].map(lambda x: aliases.get(str(x), str(x)))
    return mapped

if plx_file and crescent_file:
    # Parse raw sources
    plx_df_raw = parse_plx(plx_file)
    crescent_df_raw = parse_crescent(crescent_file)

    # Apply zero-hour filter (PLX)
    plx_df = plx_df_raw.copy()
    if hide_zero_hours:
        before = len(plx_df)
        plx_df = plx_df[plx_df["Total_Hours"] > 0]
        st.sidebar.info(f"Filtered out {before - len(plx_df)} associates with 0 hours")

    # Apply alias map to both sides BEFORE merge-and-classify (ensures roll-ups under canonical EID)
    plx_df = apply_aliases(plx_df, "EID")
    crescent_df = apply_aliases(crescent_df_raw, "EID")

    # Merge and classify discrepancies
    merged = merge_and_classify(plx_df, crescent_df, hour_tolerance=0.01)

    # Toggle: show all vs only discrepancies
    display_df = merged if show_all else merged[merged["Discrepancy"] != "Match"].reset_index(drop=True)

    # Discrepancy review with row selection
    st.subheader("Discrepancy Review")
    edited_df = st.data_editor(
        display_df,
        num_rows="dynamic",
        width="stretch",
        key="discrepancy_editor",
    )

    # --- Merge selected rows via checkbox selection in data_editor ---
    # Streamlit exposes selection via st.session_state[key]["selected_rows"]
    selected_rows = st.session_state.get("discrepancy_editor", {}).get("selected_rows", [])

    with st.expander("Merge selected rows by EID", expanded=False):
        st.write("Select rows using the left checkbox column, then enter the canonical EID.")
        canonical_eid = st.text_input("Canonical EID (digits only)", value="", key="canonical_eid_input")
        merge_btn = st.button("Apply merge to source data")

        if merge_btn:
            if not selected_rows or len(selected_rows) < 2:
                st.warning("Select at least two rows to merge.")
            elif not canonical_eid.strip():
                st.warning("Enter a canonical EID.")
            else:
                # Collect unique EIDs from selected rows
                selected_eids = set(edited_df.loc[selected_rows, "EID"].astype(str).tolist())
                # Update alias map: redirect each selected EID to the canonical one
                for old_eid in selected_eids:
                    if old_eid != canonical_eid:
                        st.session_state["eid_aliases"][old_eid] = canonical_eid

                st.success(f"Merged {len(selected_eids)} EID(s) into canonical EID {canonical_eid}.")
                st.info("Re-run comparison below to refresh the discrepancy list.")

    # Recalculate section (optional but helpful to refresh view)
    if st.button("Recalculate discrepancies"):
        # Re-apply aliases to raw sources and re-merge
        plx_df_re = apply_aliases(plx_df_raw, "EID")
        crescent_df_re = apply_aliases(crescent_df_raw, "EID")
        merged = merge_and_classify(plx_df_re, crescent_df_re, hour_tolerance=0.01)
        display_df = merged if show_all else merged[merged["Discrepancy"] != "Match"].reset_index(drop=True)
        st.success("Discrepancies recalculated.")
        st.data_editor(
            display_df,
            num_rows="dynamic",
            width="stretch",
            key="discrepancy_editor_refresh",
        )

    # Totals based on current aliasing
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
    summary_text = generate_summary(display_df)
    st.text_area("Email Summary", summary_text, height=300)
else:
    st.info("Please upload both PLX and Crescent reports.")
