def generate_summary(df):
    discrep_df = df[df["Discrepancy"] != "Match"]

    lines = []
    for _, row in discrep_df.iterrows():
        name = row.get("Name_PLX") or row.get("Name_Crescent") or "Unknown"
        correct = row.get("Total_Hours_PLX", "N/A")
        incorrect = row.get("Total_Hours_Crescent", "N/A")
        line_info = row.get("Lines", "N/A")
        badge = row.get("Badge", "N/A")
        lines.append(
            f"{name} - Worked Line(s) {line_info} for {correct} (correct), not {incorrect} (incorrect). [{badge}]"
        )
    return "\n".join(lines)
