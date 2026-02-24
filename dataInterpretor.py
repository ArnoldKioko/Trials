import pandas as pd
import numpy as np

# -------------------------
# SETTINGS
# -------------------------
INPUT_FILE = r"C:\Users\realp\OneDrive\Desktop\RSA\Projects\SAUDI EXPO\DATA\TradeData_SAUDI_HS_split.xlsx"
SHEET_NAME = 0

HS_COL = "cmdCode"      # original HS column in your file
VALUE_COL = "cifvalue"  # import value column

OUTPUT_FILE = r"C:\Users\realp\OneDrive\Desktop\RSA\Projects\SAUDI EXPO\DATA\TradeData_SAUDI_HS_analysis.xlsx"

# -------------------------
# LOAD
# -------------------------
df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME, dtype={HS_COL: "string"})

# -------------------------
# CLEAN HS (preserve leading zeros)
# -------------------------
df["HS_clean"] = (
    df[HS_COL]
    .astype("string")
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
    .str.replace(" ", "", regex=False)
)

# Ensure CIF is numeric
df[VALUE_COL] = pd.to_numeric(df[VALUE_COL], errors="coerce").fillna(0)

# HS lengths
lens = df["HS_clean"].str.len()

# Create HS2/HS4/HS6 without fabrication
df["HS2"] = df["HS_clean"].str[:2]

df["HS4"] = ""
df.loc[lens == 4, "HS4"] = df.loc[lens == 4, "HS_clean"]
df.loc[lens == 6, "HS4"] = df.loc[lens == 6, "HS_clean"].str[:4]

df["HS6"] = ""
df.loc[lens == 6, "HS6"] = df.loc[lens == 6, "HS_clean"]

# Level label
df["HS_level"] = np.select(
    [lens == 2, lens == 4, lens == 6],
    ["HS2", "HS4", "HS6"],
    default="Other"
)

# -------------------------
# 1) Aggregation comparison by level
# -------------------------
agg_hs2 = df.groupby("HS2", dropna=False)[VALUE_COL].sum().reset_index().rename(columns={"HS2": "Code"})
agg_hs2["Level"] = "HS2"

agg_hs4 = df[df["HS4"] != ""].groupby("HS4", dropna=False)[VALUE_COL].sum().reset_index().rename(columns={"HS4": "Code"})
agg_hs4["Level"] = "HS4"

agg_hs6 = df[df["HS6"] != ""].groupby("HS6", dropna=False)[VALUE_COL].sum().reset_index().rename(columns={"HS6": "Code"})
agg_hs6["Level"] = "HS6"

agg_by_level = pd.concat([agg_hs2, agg_hs4, agg_hs6], ignore_index=True)
agg_by_level = agg_by_level[["Level", "Code", VALUE_COL]].sort_values(["Level", VALUE_COL], ascending=[True, False])

# -------------------------
# 2) Rows by level (structure check)
# -------------------------
rows_by_level = (
    df.groupby("HS_level")[VALUE_COL]
      .agg(rows="count", total_cif="sum")
      .reset_index()
      .sort_values("HS_level")
)

# -------------------------
# 3) Double counting risk check
# -------------------------
total_all_rows = df[VALUE_COL].sum()
total_hs6_only = df.loc[df["HS_level"] == "HS6", VALUE_COL].sum()
inflation = total_all_rows - total_hs6_only
inflation_pct = (inflation / total_hs6_only * 100) if total_hs6_only != 0 else np.nan

double_count_check = pd.DataFrame([{
    "total_cif_all_rows": total_all_rows,
    "total_cif_hs6_only": total_hs6_only,
    "inflation_amount_if_you_sum_everything": inflation,
    "inflation_percent_vs_hs6_only": inflation_pct
}])

# -------------------------
# 4) Hierarchical tree (HS2 -> HS4 -> HS6)
#    We'll show top HS2, within each top HS4, within each top HS6
# -------------------------
tree = (
    df[df["HS_level"].isin(["HS4", "HS6"])]  # need HS4 and HS6 detail
      .groupby(["HS2", "HS4", "HS6"], dropna=False)[VALUE_COL]
      .sum()
      .reset_index()
)

# Make it readable: blank out irrelevant levels
tree.loc[tree["HS6"] == "", "HS6"] = np.nan

# Keep top 20 HS2 by total
top_hs2 = (
    df.groupby("HS2")[VALUE_COL].sum().sort_values(ascending=False).head(20).index
)
tree_top = tree[tree["HS2"].isin(top_hs2)].sort_values([VALUE_COL], ascending=False)

# -------------------------
# SAVE
# -------------------------
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Data_With_HS_Split")
    agg_by_level.to_excel(writer, index=False, sheet_name="Agg_By_Level")
    rows_by_level.to_excel(writer, index=False, sheet_name="Rows_By_Level")
    double_count_check.to_excel(writer, index=False, sheet_name="Double_Count_Check")
    tree_top.to_excel(writer, index=False, sheet_name="HS_Tree_Top")

print(f"Saved: {OUTPUT_FILE}")
