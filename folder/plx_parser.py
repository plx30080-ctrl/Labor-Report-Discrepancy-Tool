import pandas as pd

def _normalize_eid_series(s):
    # Convert to string, strip, remove trailing .0 from numeric Excel parsing
    s = s.astype(str).str.strip()
    s = s.str.replace(r"\.0$", "", regex=True)  # remove decimal suffix
    s = s.str.replace(r"\D", "", regex=True)    # keep digits only (optional, if PLX 'File' column is numeric ID)
    return s

def parse_plx(file):
    # PLX header row is row 5 in Excel (header=4)
    df = pd.read_excel(file, header=4)

    # Remove blank and total rows
    df = df.dropna(subset=["File", "Name"])
    df = df[~df["File"].astype(str).str.contains("Total", na=False)]

    # Compute total hours across weekdays (Reg + OT + DT hour columns)
    hour_cols = [c for c in df.columns if ("Reg Hrs" in c or "OT Hrs" in c or "DT Hrs" in c)]
    df["Total_Hours"] = df[hour_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)

    # Normalize EID
    df["EID"] = _normalize_eid_series(df["File"])
    df["Name"] = df["Name"].astype(str).str.strip()

    # Keep only meaningful rows with an EID
    df = df[df["EID"].str.len() > 0]

    return df[["EID", "Name", "Total_Hours"]]
