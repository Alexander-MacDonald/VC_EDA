import csv

# Define the column headers
COLUMNS = ["RANK", "NAME", "FIRM", "NOTABLE DEAL", "HEADQUARTERS"]

entries = []

with open("../data/forbes.com.txt", "r", encoding="utf-8") as file:
    lines = [line.strip() for line in file if line.strip()]

    # Read 5 lines at a time
    for i in range(0, len(lines), 5):
        chunk = lines[i:i+5]
        if len(chunk) == 5:
            entry = dict(zip(COLUMNS, chunk))
            entries.append(entry)

# Write to CSV
with open("../cleanedData/CLEAN_forbes.com.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(entries)
