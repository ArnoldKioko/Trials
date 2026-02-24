import pandas as pd
import os

# -------------------------
# SETTINGS
# -------------------------
INPUT_FILE = r"C:\Users\realp\OneDrive\Desktop\RSA\Projects\SAUDI EXPO\DATA\TradeData SAUDI expo .xlsx"
SHEET_NAME = 0
HS_COL = "cmdCode"  # <-- your HS code column
OUTPUT_FILE = r"C:\Users\realp\OneDrive\Desktop\RSA\Projects\SAUDI EXPO\DATA\TradeData_SAUDI_HS_split.xlsx"

# -------------------------s
# LOAD DATA
# -------------------------
# (No need for the if/else you had; both branches did the same thing)
df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME, dtype={HS_COL: "string"})

# -------------------------
# CLEAN + STANDARDIZE HS AS TEXT (PRESERVE LEADING ZEROS)
# -------------------------
df["HS_clean"] = (
    df[HS_COL]
    .astype("string")
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)   # if Excel stored as 3004.0
    .str.replace(" ", "", regex=False)      # remove spaces
)

# -------------------------
# DEBUG LENGTHS
# -------------------------
lens = df["HS_clean"].str.len()

print("Unique lengths found:")
print(lens.value_counts(dropna=False))

print("\nRows with invalid lengths:")
bad = df.loc[~lens.isin([2, 4, 6]), [HS_COL, "HS_clean"]].copy()
bad["Length"] = bad["HS_clean"].str.len()
print(bad.head(20))

# -------------------------
# SPLIT INTO HS2 / HS4 / HS6  (NO FABRICATION)
# -------------------------
df["HS2"] = df["HS_clean"].str[:2]

df["HS4"] = ""
df.loc[lens == 4, "HS4"] = df.loc[lens == 4, "HS_clean"]
df.loc[lens == 6, "HS4"] = df.loc[lens == 6, "HS_clean"].str[:4]

df["HS6"] = ""
df.loc[lens == 6, "HS6"] = df.loc[lens == 6, "HS_clean"]

# -------------------------
# SAVE OUTPUT
# -------------------------
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Cleaned")
    if not bad.empty:
        bad.to_excel(writer, index=False, sheet_name="Invalid_HS")

print(f"\nSaved: {OUTPUT_FILE}")
