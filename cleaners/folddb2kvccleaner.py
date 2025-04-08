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
        return None

    founding_year = block[year_index].strip()
    bio = block[year_index + 1].strip() if year_index + 1 < len(block) else ""
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

    # Separate out social links and possible firm URLs
    non_social_lines = []
    candidate_urls = []

    for line in entry_lines:
        line = line.strip()
        if not line:
            continue

        norm_line = normalize_url(line)

        if social_patterns["Twitter"].search(norm_line):
            entry["Twitter Link"] = norm_line
        elif social_patterns["LinkedIn"].search(norm_line):
            entry["LinkedIn Link"] = norm_line
        elif social_patterns["Facebook"].search(norm_line):
            entry["Facebook Link"] = norm_line
        elif "http" in norm_line or "www." in norm_line:
            candidate_urls.append(norm_line)
        else:
            non_social_lines.append(line)

    # Pick company name as first non-social line
    if non_social_lines:
        entry["Company"] = non_social_lines[0]
        non_social_lines = non_social_lines[1:]

    # Choose firm URL that is NOT a known social platform
    for url in candidate_urls:
        if not any(pattern.search(url) for pattern in social_patterns.values()):
            entry["URL"] = url
            break

    # Check last two numeric values
    if non_social_lines and non_social_lines[-1].isdigit():
        entry["Number of Exits"] = non_social_lines.pop()
    if non_social_lines and non_social_lines[-1].isdigit():
        entry["Number of Investments"] = non_social_lines.pop()

    # Now parse structured content
    field_order = ["Portfolio Companies", "Fund Type", "Fund Stage", "Fund Focus", "Location", "Description"]
    current_field = 0
    field_chunks = {field: [] for field in field_order}

    for line in non_social_lines:
        field_chunks[field_order[current_field]].append(line)
        if current_field < len(field_order) - 1 and line == "":
            current_field += 1

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
            # Peek ahead to next line (bio OR accidental URL)
            next_line = next(file, "").strip()

            # Only treat it as a bio if it's not a link or suspicious
            if next_line and not next_line.lower().startswith(("http", "www.")) and not any(social in next_line for social in ["linkedin.com", "twitter.com", "facebook.com"]):
                current_block.append(next_line)

            record = flush_entry(current_block)
            if record:
                entries.append(record)
            current_block = []

            # If the next line was a URL, treat it as part of the next entry
            if next_line and (next_line.lower().startswith(("http", "www.")) or "linkedin.com" in next_line or "twitter.com" in next_line or "facebook.com" in next_line):
                current_block.append(next_line)

# Write to CSV
with open("../cleanedData/CLEAN_folk_db_2k_vc.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    for row in entries:
        writer.writerow(row)
