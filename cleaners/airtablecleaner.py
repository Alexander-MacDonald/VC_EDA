from collections import defaultdict
import csv
import re

# Known stages, sorted by length to match longer stages first
investment_stages = ["Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Series D"]
investment_stages.sort(key=lambda x: -len(x))

# Regex to match valid lines
line_pattern = re.compile(r'^(\d+)\s+(.*)')

grouped_lines = defaultdict(list)

with open("../data/airtable.com.txt", "r") as file:
    for line in file:
        line = line.strip()
        match = line_pattern.match(line)
        if not match:
            continue
        
        key = int(match.group(1))
        content = match.group(2)

        # Find the position of the first stage in the line
        first_stage_pos = None
        first_stage = None
        for stage in investment_stages:
            idx = content.find(stage)
            if idx != -1 and (first_stage_pos is None or idx < first_stage_pos):
                first_stage_pos = idx
                first_stage = stage

        if first_stage_pos is not None:
            company = content[:first_stage_pos].strip()
            rest = content[first_stage_pos:].strip()

            # Extract all the stages from the rest of the line
            stages = []
            for stage in investment_stages:
                if stage in rest:
                    stages.append(stage)

            grouped_lines[key].append([company] + stages)
        else:
            # No known stage found; just store full content
            grouped_lines[key].append([content])

with open("../cleanedData./CLEAN_airtable.com.csv", "w", newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)

    # Write header (optional)
    writer.writerow(["ID", "Company", "Stages", "Line 1", "Line 2", "Line 3", "Line 4"])

    for key in sorted(grouped_lines):
        entries = grouped_lines[key]
        
        # First entry is assumed to be [company, stage1, stage2, ...]
        if not entries or len(entries[0]) < 2:
            continue  # Skip if malformed

        company = entries[0][0]
        stages = entries[0][1:]

        # The rest of the lines (convert list to string)
        additional_lines = [line[0] if isinstance(line, list) and len(line) == 1 else str(line) for line in entries[1:]]

        # Fill missing columns with empty strings to keep columns aligned
        while len(additional_lines) < 4:
            additional_lines.append("")

        row = [key, company, str(stages)] + additional_lines[:4]
        writer.writerow(row)