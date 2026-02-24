import pandas as pd
import numpy as np

# ============================================================
# PURPOSE
# - Split mixed HS codes into HS2/HS4/HS6 (no fabrication)
# - THEN (Option B) build a clean hierarchy using ONLY HS6 rows
#   to avoid double counting / inconsistent totals.
# - Export to one Excel with multiple sheets.
# ============================================================

# -------------------------
# SETTINGS (EDIT THESE)
# -------------------------
INPUT_FILE = r"C:\Users\realp\OneDrive\Desktop\RSA\Projects\SAUDI EXPO\DATA\TradeData SAUDI expo .xlsx"
SHEET_NAME = 0

HS_COL = "cmdCode"        # HS code column (mixed 2/4/6)
VALUE_COL = "cifvalue"    # import value column

OUTPUT_FILE = r"C:\Users\realp\OneDrive\Desktop\RSA\Projects\SAUDI EXPO\DATA\TradeData_SAUDI_HS_RebuiltHierarchy.xlsx"

# -------------------------
# LOAD
# -------------------------
df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME, dtype={HS_COL: "string"})

# -------------------------
# CLEAN HS AS TEXT (PRESERVE LEADING ZEROS)
# -------------------------
df["HS_clean"] = (
    df[HS_COL]
    .astype("string")
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)  # handles 3004.0 if it appears
    .str.replace(" ", "", regex=False)
)

# Ensure CIF is numeric
df[VALUE_COL] = pd.to_numeric(df[VALUE_COL], errors="coerce").fillna(0)

# Lengths and level labels
lens = df["HS_clean"].str.len()

df["HS_level"] = np.select(
    [lens == 2, lens == 4, lens == 6],
    ["HS2", "HS4", "HS6"],
    default="Other"
)

# -------------------------
# SPLIT INTO HS2 / HS4 / HS6 (NO FABRICATION)
# -------------------------
df["HS2"] = df["HS_clean"].str[:2]

df["HS4"] = ""
df.loc[lens == 4, "HS4"] = df.loc[lens == 4, "HS_clean"]
df.loc[lens == 6, "HS4"] = df.loc[lens == 6, "HS_clean"].str[:4]

df["HS6"] = ""
df.loc[lens == 6, "HS6"] = df.loc[lens == 6, "HS_clean"]

# -------------------------
# DEBUG: SHOW INVALID HS LENGTHS (IF ANY)
# -------------------------
invalid = df.loc[~lens.isin([2, 4, 6]), [HS_COL, "HS_clean", VALUE_COL, "HS_level"]].copy()
if not invalid.empty:
    invalid["Length"] = invalid["HS_clean"].str.len()

print("HS length counts:")
print(lens.value_counts(dropna=False))
if not invalid.empty:
    print("\nSample invalid HS rows (first 20):")
    print(invalid.head(20))

# ============================================================
# OPTION B: REBUILD THE HIERARCHY FROM HS6 ONLY
# ============================================================

# Use ONLY HS6 rows as the “truth” layer
df_hs6 = df[df["HS_level"] == "HS6"].copy()

# Rebuild HS4 and HS2 directly from HS6
df_hs6["HS4_rebuilt"] = df_hs6["HS6"].str[:4]
df_hs6["HS2_rebuilt"] = df_hs6["HS6"].str[:2]

# -------------------------
# REBUILT TOTALS (CONSISTENT)
# -------------------------

# HS6 totals
hs6_totals = (
    df_hs6.groupby("HS6", dropna=False)[VALUE_COL]
    .sum()
    .reset_index()
    .sort_values(VALUE_COL, ascending=False)
)

# HS4 totals rebuilt from HS6
hs4_totals = (
    df_hs6.groupby("HS4_rebuilt", dropna=False)[VALUE_COL]
    .sum()
    .reset_index()
    .rename(columns={"HS4_rebuilt": "HS4"})
    .sort_values(VALUE_COL, ascending=False)
)

# HS2 totals rebuilt from HS6
hs2_totals = (
    df_hs6.groupby("HS2_rebuilt", dropna=False)[VALUE_COL]
    .sum()
    .reset_index()
    .rename(columns={"HS2_rebuilt": "HS2"})
    .sort_values(VALUE_COL, ascending=False)
)

# -------------------------
# TREE (HS2 -> HS4 -> HS6) BUILT ONLY FROM HS6
# -------------------------
tree = (
    df_hs6.groupby(["HS2_rebuilt", "HS4_rebuilt", "HS6"], dropna=False)[VALUE_COL]
    .sum()
    .reset_index()
    .rename(columns={"HS2_rebuilt": "HS2", "HS4_rebuilt": "HS4"})
    .sort_values([VALUE_COL], ascending=False)
)

# Optional: show only top HS2 chapters by value (keeps file manageable)
top_hs2 = hs2_totals["HS2"].head(20).tolist()
tree_top = tree[tree["HS2"].isin(top_hs2)].copy()

# -------------------------
# DOUBLE COUNT CHECK (WHY WE DO OPTION B)
# -------------------------
total_all_rows = df[VALUE_COL].sum()
total_hs6_only = df_hs6[VALUE_COL].sum()
inflation = total_all_rows - total_hs6_only
inflation_pct = (inflation / total_hs6_only * 100) if total_hs6_only != 0 else np.nan

double_count_check = pd.DataFrame([{
    "total_cif_all_rows_(mixed_levels)": total_all_rows,
    "total_cif_hs6_only_(recommended)": total_hs6_only,
    "inflation_if_you_sum_mixed_levels": inflation,
    "inflation_percent_vs_hs6_only": inflation_pct
}])

# -------------------------
# SAVE OUTPUT (ONE EXCEL FILE)
# -------------------------
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    # Base data
    df.to_excel(writer, index=False, sheet_name="Data_With_HS_Split")
    if not invalid.empty:
        invalid.to_excel(writer, index=False, sheet_name="Invalid_HS")

    # Rebuilt hierarchy outputs
    df_hs6.to_excel(writer, index=False, sheet_name="HS6_BaseData")
    hs6_totals.to_excel(writer, index=False, sheet_name="HS6_Totals")
    hs4_totals.to_excel(writer, index=False, sheet_name="HS4_Rebuilt_Totals")
    hs2_totals.to_excel(writer, index=False, sheet_name="HS2_Rebuilt_Totals")
    tree_top.to_excel(writer, index=False, sheet_name="Tree_Top_HS2")
    double_count_check.to_excel(writer, index=False, sheet_name="DoubleCount_Check")

print(f"\nSaved: {OUTPUT_FILE}")
