import pandas as pd

def compare_reports(plx_df, crescent_df):
    merged = pd.merge(plx_df, crescent_df, on="EID", how="outer", suffixes=("_PLX", "_Crescent"), indicator=True)

    def categorize(row):
        if row["_merge"] == "left_only":
            return "PLX-only"
        elif row["_merge"] == "right_only":
            return "Crescent-only"
        elif pd.isnull(row["Total_Hours_PLX"]) or pd.isnull(row["Total_Hours_Crescent"]):
            return "Invalid EID"
        elif row["Total_Hours_PLX"] != row["Total_Hours_Crescent"]:
            return "Mismatched Hours"
        else:
            return "Match"

    merged["Discrepancy"] = merged.apply(categorize, axis=1)
    merged["Resolution"] = ""
    merged["Notes"] = ""
    return merged
