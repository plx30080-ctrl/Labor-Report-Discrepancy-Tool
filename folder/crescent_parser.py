import pandas as pd

def _normalize_eid_series(s):
    s = s.astype(str).str.strip()
    s = s.str.replace(r"\D", "", regex=True)  # keep digits only
    return s

def parse_crescent(file):
    # Load file
    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
    df.columns = df.columns.str.strip()

    # Identify key columns
    badge_col = next((c for c in df.columns if "Badge" in c or "badge" in c), None)
    line_col = next((c for c in df.columns if "Line" in c or "line" in c), None)
    hours_col = next((c for c in df.columns if "Hours" in c or "hours" in c), None)

    if not badge_col or not line_col or not hours_col:
        raise ValueError(f"Crescent file missing required columns. Found: {df.columns.tolist()}")

    # Extract EID from Badge
    df["EID"] = df[badge_col].astype(str).str.extract(r"PLX-(\d+)-")[0]
    df["EID"] = _normalize_eid_series(df["EID"])
    df = df[df["EID"].str.len() > 0]

    # Clean hours
    df["Hours"] = pd.to_numeric(df[hours_col], errors="coerce").fillna(0)

    # Aggregate by EID: sum hours, concat lines, concat badges
    grouped = df.groupby("EID").agg(
        Total_Hours=("Hours", "sum"),
        Lines=(line_col, lambda x: ", ".join(sorted(set(x.astype(str))))),
        Badge=(badge_col, lambda x: ", ".join(sorted(set(x.astype(str)))))
    ).reset_index()

    grouped["Name"] = ""  # placeholder for consistency

    return grouped[["EID", "Name", "Total_Hours", "Lines", "Badge"]]
