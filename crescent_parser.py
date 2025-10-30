import pandas as pd

def parse_crescent(file):
    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
    df = df.dropna(subset=["Badge", "Payable Hours"])
    df["EID"] = df["Badge"].str.extract(r"PLX-(\d+)-")[0]
    df["Total_Hours"] = df["Payable Hours"]
    df["Name"] = ""
    return df[["EID", "Name", "Total_Hours", "Badge", "Line"]]
