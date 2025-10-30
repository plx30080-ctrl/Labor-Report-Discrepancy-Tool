import pandas as pd

def merge_and_classify(plx_df, crescent_df, hour_tolerance=0.01):
    """
    Merge PLX and Crescent dataframes on EID and classify discrepancies.

    Parameters
    ----------
    plx_df : pd.DataFrame
        Columns: EID, Name, Total_Hours
    crescent_df : pd.DataFrame
        Columns: EID, Name, Total_Hours, Lines (optional)
    hour_tolerance : float
        Allowed difference in hours before flagging mismatch

    Returns
    -------
    pd.DataFrame
        Combined dataframe with discrepancy classification and workflow columns
    """

    # Outer merge to capture all EIDs
    merged = pd.merge(
        plx_df,
        crescent_df,
        on="EID",
        how="outer",
        suffixes=("_PLX", "_Crescent"),
        indicator=True
    )

    # Ensure numeric hours
    merged["Total_Hours_PLX"] = pd.to_numeric(merged.get("Total_Hours_PLX"), errors="coerce")
    merged["Total_Hours_Crescent"] = pd.to_numeric(merged.get("Total_Hours_Crescent"), errors="coerce")

    def categorize(row):
        merge_state = row["_merge"]

        if merge_state == "left_only":
            # Exists in PLX but not in Crescent
            return "No EID on Crescent"
        if merge_state == "right_only":
            # Exists in Crescent but not in PLX
            return "Crescent-only"

        th_plx = row["Total_Hours_PLX"]
        th_cres = row["Total_Hours_Crescent"]

        if pd.isna(th_plx) or pd.isna(th_cres):
            return "Invalid data"

        if abs(float(th_plx) - float(th_cres)) > hour_tolerance:
            return "Mismatched Hours"

        return "Match"

    merged["Discrepancy"] = merged.apply(categorize, axis=1)

    # Add workflow columns
    merged["Resolution"] = ""
    merged["Notes"] = ""

    # Sort so discrepancies appear first
    sort_order = pd.CategoricalDtype(
        ["Mismatched Hours", "No EID on Crescent", "Crescent-only", "Invalid data", "Match"],
        ordered=True
    )
    merged["Discrepancy"] = merged["Discrepancy"].astype(sort_order)
    merged = merged.sort_values("Discrepancy").reset_index(drop=True)

    return merged
