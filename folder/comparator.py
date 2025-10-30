import pandas as pd

def merge_and_classify(plx_df, crescent_df, hour_tolerance=0.01):
    # Outer merge so we can see all categories; keep names and hours from both sides
    merged = pd.merge(
        plx_df, crescent_df,
        on="EID", how="outer",
        suffixes=("_PLX", "_Crescent"),
        indicator=True
    )

    # Discrepancy categories:
    # 1) Mismatched Hours: same EID on both, hours differ beyond tolerance
    # 2) PLX-only or Crescent-only: EID on one file only
    # 3) No EID found on Crescent file: present in PLX, missing in Crescent (subset of PLX-only, labeled distinctly)

    def categorize(row):
        merge_state = row["_merge"]
        th_plx = row.get("Total_Hours_PLX")
        th_cres = row.get("Total_Hours_Crescent")

        if merge_state == "left_only":
            # specifically call out no EID in Crescent for clarity
            return "No EID on Crescent"
        if merge_state == "right_only":
            return "Crescent-only"

        # Both sides present
        if pd.isna(th_plx) or pd.isna(th_cres):
            return "Invalid data"
        if abs(float(th_plx) - float(th_cres)) > hour_tolerance:
            return "Mismatched Hours"
        return "Match"

    merged["Discrepancy"] = merged.apply(categorize, axis=1)

    # Convenience columns for UI
    merged["Resolution"] = ""
    merged["Notes"] = ""

    # Sort to show discrepancies first
    sort_order = pd.CategoricalDtype(
        ["Mismatched Hours", "No EID on Crescent", "Crescent-only", "Match", "Invalid data"],
        ordered=True
    )
    merged["Discrepancy"] = merged["Discrepancy"].astype(sort_order)
    merged = merged.sort_values("Discrepancy").reset_index(drop=True)

    return merged
