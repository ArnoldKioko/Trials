import pandas as pd
import numpy as np

# ============================================================
# SCENARIO 4 ONLY (FIXED): HIERARCHICAL TREE FROM HS6 ONLY
# - Uses ONLY HS6 rows to avoid double counting / inconsistent totals
# - Builds HS2 -> HS4 -> HS6 tree with CIF totals
# - Adds product/row names (descriptions) so you understand each code
# ============================================================

# -------------------------
# SETTINGS (EDIT THESE)
# -------------------------
INPUT_FILE = r"C:\Users\realp\OneDrive\Desktop\RSA\Projects\SAUDI EXPO\DATA\TradeData SAUDI expo .xlsx"
SHEET_NAME = 0

HS_COL = "cmdCode"        # HS code column (mixed 2/4/6)
VALUE_COL = "cifvalue"    # import value column
DESC_COL = "cmdDesc"          # put your description column name here if it exists (e.g., "cmdDescName" or "cmdName")

OUTPUT_FILE = r"C:\Users\realp\OneDrive\Desktop\RSA\Projects\SAUDI EXPO\DATA\TradeData_SAUDI_Tree_HS6Only.xlsx"

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
    .str.replace(r"\.0$", "", regex=True)
    .str.replace(" ", "", regex=False)
)

# CIF numeric
df[VALUE_COL] = pd.to_numeric(df[VALUE_COL], errors="coerce").fillna(0)

# Identify HS level by length
lens = df["HS_clean"].str.len()
df["HS_level"] = np.select([lens == 2, lens == 4, lens == 6], ["HS2", "HS4", "HS6"], default="Other")

# HS6 base only (this is the fix)
df_hs6 = df[df["HS_level"] == "HS6"].copy()

# Rebuild HS4 and HS2 from HS6
df_hs6["HS6"] = df_hs6["HS_clean"]
df_hs6["HS4"] = df_hs6["HS6"].str[:4]
df_hs6["HS2"] = df_hs6["HS6"].str[:2]

# -------------------------
# ADD "ROW NAMES" / PRODUCT NAMES
# -------------------------
# If you have a description column, set DESC_COL above and we will use it.
# If you don't, we will still create readable labels like "HS6 271019".
if DESC_COL and DESC_COL in df_hs6.columns:
    # Take the most common description per code (mode)
    hs6_name = (df_hs6.groupby("HS6")[DESC_COL]
                .agg(lambda s: s.mode().iat[0] if not s.mode().empty else s.dropna().iloc[0] if len(s.dropna()) else "")
                .reset_index()
                .rename(columns={DESC_COL: "HS6_Name"}))

    hs4_name = (df_hs6.groupby("HS4")[DESC_COL]
                .agg(lambda s: s.mode().iat[0] if not s.mode().empty else s.dropna().iloc[0] if len(s.dropna()) else "")
                .reset_index()
                .rename(columns={DESC_COL: "HS4_Name"}))

    hs2_name = (df_hs6.groupby("HS2")[DESC_COL]
                .agg(lambda s: s.mode().iat[0] if not s.mode().empty else s.dropna().iloc[0] if len(s.dropna()) else "")
                .reset_index()
                .rename(columns={DESC_COL: "HS2_Name"}))
else:
    hs6_name = pd.DataFrame({"HS6": df_hs6["HS6"].unique()})
    hs6_name["HS6_Name"] = "HS6 " + hs6_name["HS6"]

    hs4_name = pd.DataFrame({"HS4": df_hs6["HS4"].unique()})
    hs4_name["HS4_Name"] = "HS4 " + hs4_name["HS4"]

    hs2_name = pd.DataFrame({"HS2": df_hs6["HS2"].unique()})
    hs2_name["HS2_Name"] = "HS2 " + hs2_name["HS2"]

# -------------------------
# BUILD TREE: HS2 -> HS4 -> HS6 (CIF totals)
# -------------------------
tree = (
    df_hs6.groupby(["HS2", "HS4", "HS6"], dropna=False)[VALUE_COL]
    .sum()
    .reset_index()
    .rename(columns={VALUE_COL: "CIF_Total"})
)

# Merge in names
tree = tree.merge(hs2_name, on="HS2", how="left")
tree = tree.merge(hs4_name, on="HS4", how="left")
tree = tree.merge(hs6_name, on="HS6", how="left")

# Reorder columns for readability
tree = tree[["HS2", "HS2_Name", "HS4", "HS4_Name", "HS6", "HS6_Name", "CIF_Total"]]
tree = tree.sort_values(["HS2", "HS4", "CIF_Total"], ascending=[True, True, False])

# Optional: also create HS2 and HS4 subtotals derived from HS6 (for easier reading)
hs2_totals = tree.groupby(["HS2", "HS2_Name"], dropna=False)["CIF_Total"].sum().reset_index().sort_values("CIF_Total", ascending=False)
hs4_totals = tree.groupby(["HS2", "HS2_Name", "HS4", "HS4_Name"], dropna=False)["CIF_Total"].sum().reset_index().sort_values("CIF_Total", ascending=False)

# -------------------------
# SAVE
# -------------------------
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    tree.to_excel(writer, index=False, sheet_name="Tree_HS2_HS4_HS6")
    hs4_totals.to_excel(writer, index=False, sheet_name="HS4_Totals_From_HS6")
    hs2_totals.to_excel(writer, index=False, sheet_name="HS2_Totals_From_HS6")

print(f"Saved: {OUTPUT_FILE}")
