import pandas as pd

def parse_plx(file):
    df = pd.read_excel(file, header=4)
    df = df.dropna(subset=["File", "Name"])
    df = df[~df["File"].astype(str).str.contains("Total", na=False)]

    weekday_cols = [col for col in df.columns if "Reg Hrs" in col or "OT Hrs" in col]
    df["Total_Hours"] = df[weekday_cols].sum(axis=1)
    df["EID"] = df["File"].astype(str)
    df["Name"] = df["Name"].astype(str)
    return df[["EID", "Name", "Total_Hours"]]
