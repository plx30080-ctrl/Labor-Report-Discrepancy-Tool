import pandas as pd

def _normalize_eid_series(s):
    s = s.astype(str).str.strip()
    s = s.str.replace(r"\D", "", regex=True)  # keep digits only
    return s

def parse_crescent(file):
    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
    df.columns = df.columns.str.strip().str.lower()

    # Identify columns
    possible_hour_cols = ["payable hours", "payable_hours", "hours", "total hours"]
    hour_col = next((c for c in df.columns if c in possible_hour_cols), None)
    badge_col = next((c for c in df.columns if "badge" in c), None)
    line_col = next((c for c in df.columns if "Line name" in c), None)

    # Extract EID
    df["EID"] = df[badge_col].str.extract(r"PLX-(\d+)-")[0]
    df["EID"] = _normalize_eid_series(df["EID"])
    df = df[df["EID"].str.len() > 0]

    # Hours
    df["Total_Hours"] = pd.to_numeric(df[hour_col], errors="coerce").fillna(0)
    df["Name"] = ""

    # ✅ Aggregate by EID, summing hours and concatenating lines
    grouped = df.groupby("EID", as_index=False).agg({
        "Total_Hours": "sum",
        line_col: lambda x: ", ".join(sorted(set(x.dropna().astype(str))))
    })

    grouped["Name"] = ""
    grouped = grouped.rename(columns={line_col: "Lines"})

    return grouped[["EID", "Name", "Total_Hours", "Lines"]]
