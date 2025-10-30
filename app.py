🧠 Reference Prompt: Labor Report Comparison Tool (ProLogistix vs. Crescent)

Goal:
Build a user-friendly Streamlit app (Python) that compares two labor reports — one from ProLogistix (PLX) and one from Crescent — to identify and resolve discrepancies in employee hours worked.

🧾 Step-by-Step Objectives

Upload Input Files

Upload PLX and Crescent reports.

PLX file types: .xls or .xlsx

Crescent file types: .csv or .xlsx

Normalize Data

Convert each dataset into a unified structure.

Automatically extract EID, Name, and weekly/daily hours.

Remove total and blank rows.

Compare & Edit

Display each dataset using Streamlit’s data editor.

Allow manual edits (hours, name, line, etc.).

Recalculate totals dynamically.

Detect Discrepancies

Match employees by EID.

Categorize differences into:

PLX-only: Exists in PLX, not in Crescent.

Crescent-only: Exists in Crescent, not in PLX.

Mismatched Hours: Same EID, different hours.

Invalid EIDs: Bad or missing IDs in Crescent file.

User Review Workflow

Allow marking discrepancies as:

Resolved ✅

Crescent Error ⚠️

Badge Correction Needed 🪪

Add manual notes per row.

Validation

After resolving discrepancies:

Recalculate totals.

Display “✅ Totals match” or “⚠️ Difference of X hours”.

Client Summary Output

Generate an email summary for Crescent:

Associate Name - Worked Line X for # (correct), not # (incorrect). [Badge Number]


Design & Usability

Modern, clean Streamlit UI.

Sidebar for:

File uploads.

Day-of-week filter (All, Monday–Saturday).

Visual feedback on matching vs. mismatched totals.

Uses width='stretch' instead of deprecated use_container_width.

🧩 Data Structure Details

ProLogistix Report (PLX)

Header row: row 5 (i.e., header=4 in pandas)

Columns:

Dept, File (EID), Name, Bill Rate

Per weekday: repeating columns for
Reg Hrs, Reg $, OT Hrs, OT $, DT Hrs, DT $

Total_Hours = sum of all weekday (Reg + OT) hours.

Crescent Report

Columns:

Badge (format: PLX-########-ABC)

Payable Hours

Line

EID extracted from Badge (digits between PLX- and -ABC).
