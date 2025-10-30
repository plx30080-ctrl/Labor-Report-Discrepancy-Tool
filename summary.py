def generate_summary(df):
    summary = []
    for _, row in df[df["Discrepancy"] != "Match"].iterrows():
        correct = row.get("Total_Hours_PLX", "N/A")
        incorrect = row.get("Total_Hours_Crescent", "N/A")
        line = row.get("Line", "N/A")
        badge = row.get("Badge", "N/A")
        name = row.get("Name_PLX") or row.get("Name_Crescent", "Unknown")
        summary.append(f"{name} - Worked Line {line} for {correct} (correct), not {incorrect} (incorrect). [{badge}]")
    return "\n".join(summary)
