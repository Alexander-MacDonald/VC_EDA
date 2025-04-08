import pandas as pd
from rapidfuzz import fuzz, process
import os
from collections import defaultdict

# Step 1: Load all CSVs into dataframes
folder = "cleanedData"
csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
dfs = []

# Map alternate name fields to "Firm"
name_columns = ["Firm", "Company", "FIRM", "NAME"]
canonical_name = "Firm"

for file in csv_files:
    df = pd.read_csv(os.path.join(folder, file), dtype=str)
    
    # Normalize name column
    for col in name_columns:
        if col in df.columns:
            df[canonical_name] = df[col]
            break
    dfs.append(df)

# Step 2: Combine all dataframes
combined_df = pd.concat(dfs, ignore_index=True).dropna(subset=[canonical_name])

# Step 3: Fuzzy group similar firm names
firm_names = combined_df[canonical_name].dropna().unique()
firm_map = {}  # maps alias → canonical name
processed = set()

for name in firm_names:
    if name in processed:
        continue
    matches = process.extract(name, firm_names, scorer=fuzz.token_sort_ratio, limit=10)
    for match, score, _ in matches:
        if score > 90:  # You can lower or raise this threshold
            firm_map[match] = name
            processed.add(match)

# Step 4: Apply the firm name deduplication map
combined_df[canonical_name] = combined_df[canonical_name].map(firm_map).fillna(combined_df[canonical_name])

# Step 5: Group by firm name, combine data
grouped_data = defaultdict(dict)

for _, row in combined_df.iterrows():
    firm = row[canonical_name]
    for col in combined_df.columns:
        val = row[col]
        if pd.notna(val) and val != firm:
            existing = grouped_data[firm].get(col, "")
            if val not in existing:
                grouped_data[firm][col] = f"{existing}, {val}".strip(", ")

# Step 6: Build final dataframe
final_rows = []

all_columns = set(combined_df.columns)

for firm, data in grouped_data.items():
    row = {col: data.get(col, "") for col in all_columns}
    row[canonical_name] = firm
    final_rows.append(row)

final_df = pd.DataFrame(final_rows)
columns = ["Firm"] + [col for col in final_df.columns if col != "Firm"]
final_df = final_df[columns]
final_df.to_csv("vc_data_dump.csv", index=False)
