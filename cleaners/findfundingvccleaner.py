import re
import csv

# Known stages
investment_stages = ["Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Series D"]
stage_set = set(investment_stages)

# Regex patterns for disruptors
disruptor_patterns = [
    re.compile(r'\bwebsite\b', re.IGNORECASE),
    re.compile(r'🔍 Find an intro'),
    re.compile(r'\d{1,2}/\d{1,2}/\d{2},\s+\d{1,2}:\d{2}\s*(AM|PM)', re.IGNORECASE),  # dates like 4/3/25, 4:57 PM
    re.compile(r'\b\d{1,3}/101\b'),  # 99/101
    re.compile(r'findfunding\.vc', re.IGNORECASE),
    re.compile(r'https?://'),  # URLs
]

def is_stage_line(line):
    tokens = line.strip().split()
    return all(token in stage_set for token in tokens) and tokens != []

def is_disruptor(line):
    return any(p.search(line) for p in disruptor_patterns)

entries = []
current_entry = []

with open("../data/findfunding.vc.txt", "r", encoding="utf-8") as file:
    for line in file:
        stripped = line.strip()
        if not stripped or is_disruptor(stripped):
            continue  # Skip empty or disruptive lines

        current_entry.append(stripped)

        if is_stage_line(stripped):
            if len(current_entry) >= 2:
                company = current_entry[0]
                stages = current_entry[-1].split()
                description = " ".join(current_entry[1:-1])
                entries.append({
                    'Company': company,
                    'Stages': stages,
                    'Description': description
                })
            current_entry = []

# Save to CSV
with open("../cleanedData/CLEAN_findfundingvccleaner.csv", "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Company", "Stages", "Description"])
    for entry in entries:
        writer.writerow([entry['Company'], str(entry['Stages']), entry['Description']])
