import pandas as pd

def parse_crescent(file):
    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    # Normalize column names (strip spaces, lowercase)
    df.columns = df.columns.str.strip().str.lower()

    # Try to find the hours column
    possible_hour_cols = ["payable hours", "payable_hours", "hours", "total hours"]
    hour_col = next((col for col in df.columns if col in possible_hour_cols), None)

    if hour_col is None:
        raise ValueError(f"Crescent file missing expected hours column. Found: {df.columns.tolist()}")

    # Badge column
    badge_col = next((col for col in df.columns if "badge" in col), None)
    if badge_col is None:
        raise ValueError(f"Crescent file missing 'Badge' column. Found: {df.columns.tolist()}")

    df["EID"] = df[badge_col].str.extract(r"PLX-(\d+)-")[0]
    df["Total_Hours"] = df[hour_col]
    df["Name"] = ""
    return df[["EID", "Name", "Total_Hours", badge_col]]
