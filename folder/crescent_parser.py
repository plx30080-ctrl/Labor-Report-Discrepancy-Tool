import pandas as pd

def _normalize_eid_series(s):
    s = s.astype(str).str.strip()
    s = s.str.replace(r"\D", "", regex=True)  # keep digits only from extracted EID
    return s

def parse_crescent(file):
    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Resolve hours column flexibly
    possible_hour_cols = ["payable hours", "payable_hours", "hours", "total hours"]
    hour_col = next((c for c in df.columns if c in possible_hour_cols), None)
    if hour_col is None:
        raise ValueError(f"Crescent file missing expected hours column. Found: {df.columns.tolist()}")

    # Badge column
    badge_col = next((c for c in df.columns if "badge" in c), None)
    if badge_col is None:
        raise ValueError(f"Crescent file missing 'Badge' column. Found: {df.columns.tolist()}")

    # Extract EID digits between PLX- and -ABC-like suffix
    df["EID"] = df[badge_col].str.extract(r"PLX-(\d+)-")[0]
    df["EID"] = _normalize_eid_series(df["EID"])

    # Keep only rows with valid EID
    df = df[df["EID"].str.len() > 0]

    # Build normalized structure
    df["Total_Hours"] = pd.to_numeric(df[hour_col], errors="coerce").fillna(0)
    df["Name"] = ""  # optional; will use PLX name in merges if available

    return df[["EID", "Name", "Total_Hours", badge_col]].rename(columns={badge_col: "Badge"})
