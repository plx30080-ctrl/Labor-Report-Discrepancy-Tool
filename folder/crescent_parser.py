import pandas as pd

def _normalize_eid_series(s):
    s = s.astype(str).str.strip()
    s = s.str.replace(r"\D", "", regex=True)  # keep digits only
    return s

def parse_crescent(file):
    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
    df.columns = df.columns.str.strip()

    # Identify badge column
    badge_col = next((c for c in df.columns if "Badge" in c or "badge" in c), None)
    if badge_col is None:
        raise ValueError(f"Crescent file missing 'Badge' column. Found: {df.columns.tolist()}")

    # Extract EID
    df["EID"] = df[badge_col].astype(str).str.extract(r"PLX-(\d+)-")[0]
    df["EID"] = _normalize_eid_series(df["EID"])
    df = df[df["EID"].str.len() > 0]

    # Assume all columns except Badge/EID are line columns
    line_cols = [c for c in df.columns if c not in [badge_col, "EID"]]

    # Melt so each line column becomes a row
    melted = df.melt(
        id_vars=["EID", badge_col],
        value_vars=line_cols,
        var_name="Line",
        value_name="Hours"
    )

    # Clean hours
    melted["Hours"] = pd.to_numeric(melted["Hours"], errors="coerce").fillna(0)

    # Aggregate: total hours per EID, plus concatenated lines
    grouped = melted.groupby("EID").agg(
        Total_Hours=("Hours", "sum"),
        Lines=("Line", lambda x: ", ".join(sorted(set(x[melted.loc[x.index, "Hours"] > 0].astype(str)))))
    ).reset_index()

    grouped["Name"] = ""  # placeholder for consistency
    grouped["Badge"] = ""  # optional, if you want to preserve one badge per EID

    return grouped[["EID", "Name", "Total_Hours", "Lines"]]
