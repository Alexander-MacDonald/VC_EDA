import re
import csv

# Define expected columns in order
COLUMNS = [
    "URL", "Company", "Portfolio Companies", "Fund Type", "Fund Stage",
    "Fund Focus", "Location", "Twitter Link", "LinkedIn Link", "Facebook Link",
    "Number of Investments", "Number of Exits", "Description", "Founding Year", "Bio"
]

# Pattern to detect a founding year (2000-2025 range as a proxy)
founding_year_pattern = re.compile(r'\b(18|19|20)\d{2}\b')

entries = []
current_block = []

def normalize_url(url):
    url = url.strip()
    if url and not url.startswith(("http://", "https://")):
        if url.startswith("www."):
            return "http://" + url
    return url

social_patterns = {
    "Twitter": re.compile(r'twitter\.com', re.IGNORECASE),
    "LinkedIn": re.compile(r'linkedin\.com', re.IGNORECASE),
    "Facebook": re.compile(r'facebook\.com', re.IGNORECASE),
}

def flush_entry(block):
    if not block:
        return None

    # Find founding year line
    try:
        year_index = next(i for i, line in enumerate(block) if founding_year_pattern.fullmatch(line.strip()))
    except StopIteration:
        return None  # skip if no founding year

    # Extract year and bio
    founding_year = block[year_index].strip()
    bio = block[year_index + 1].strip() if year_index + 1 < len(block) else ""

    # Entry block ends before year
    entry_lines = block[:year_index]

    entry = {
        "Founding Year": founding_year,
        "Bio": bio,
        "URL": "",
        "Company": "",
        "Portfolio Companies": "",
        "Fund Type": "",
        "Fund Stage": "",
        "Fund Focus": "",
        "Location": "",
        "Twitter Link": "",
        "LinkedIn Link": "",
        "Facebook Link": "",
        "Number of Investments": "",
        "Number of Exits": "",
        "Description": ""
    }

    # Basic URL detection
    first_line = normalize_url(entry_lines[0])
    if "://" in first_line:
        entry["URL"] = first_line
        entry["Company"] = entry_lines[1].strip() if len(entry_lines) > 1 else ""
        idx = 2
    else:
        entry["URL"] = ""
        entry["Company"] = entry_lines[0].strip()
        idx = 1

    rest = entry_lines[idx:]

    # Split numeric fields (from bottom)
    if rest and rest[-1].isdigit():
        entry["Number of Exits"] = rest.pop()
    if rest and rest[-1].isdigit():
        entry["Number of Investments"] = rest.pop()

    # Split out social links from the remaining lines
    non_social_lines = []
    for line in rest:
        line = line.strip()
        if social_patterns["Twitter"].search(line):
            entry["Twitter Link"] = line
        elif social_patterns["LinkedIn"].search(line):
            entry["LinkedIn Link"] = line
        elif social_patterns["Facebook"].search(line):
            entry["Facebook Link"] = line
        else:
            non_social_lines.append(line)

    # Now process the remaining "content" lines
    field_order = ["Portfolio Companies", "Fund Type", "Fund Stage", "Fund Focus", "Location", "Description"]
    current_field = 0
    field_chunks = {field: [] for field in field_order}

    for line in non_social_lines:
        field_chunks[field_order[current_field]].append(line)
        # Optional: change this logic if you have a smarter way to determine where one field ends
        if current_field < len(field_order) - 1 and line == "":
            current_field += 1

    # Assign the collected chunks to the fields
    for field in field_order:
        joined = ", ".join([l for l in field_chunks[field] if l])
        entry[field] = joined.strip()

    return entry

# Read and process the file
with open("../data/folk_db_2k_vc.txt", "r", encoding="utf-8") as file:
    for line in file:
        stripped = line.strip()
        if not stripped:
            continue  # skip blank lines
        current_block.append(stripped)

        if founding_year_pattern.fullmatch(stripped):
            # Likely end of an entry, grab one more line for bio
            next_line = next(file, "").strip()
            if next_line:
                current_block.append(next_line)

            record = flush_entry(current_block)
            if record:
                entries.append(record)
            current_block = []

# Write to CSV
with open("../cleanedData/CLEAN_folk_db_2k_vc.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    for row in entries:
        writer.writerow(row)
