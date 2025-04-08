import re
import csv
from html import unescape

# Read the raw HTML-ish .txt file
with open("../data/projectstartups.com.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Find all firm "cards"
cards = re.findall(r'<div class="card mb-3">(.*?)</div>\s*</div>', text, re.DOTALL)

entries = []

for card in cards:
    # Extract the firm name from <a> tag inside card-title
    firm_match = re.search(r'<h5 class="card-title">.*?<a .*?>(.*?)</a>', card, re.DOTALL)
    firm_name = unescape(firm_match.group(1).strip()) if firm_match else ""

    # Extract the card-text contents
    text_match = re.search(r'<p class="card-text">(.*?)</p>', card, re.DOTALL)
    card_text = unescape(text_match.group(1).strip()) if text_match else ""

    # Split card-text by <br>
    sections = [section.strip() for section in card_text.split('<br>') if section.strip()]
    info = {"Firm": firm_name, "Offices": "", "Stages": "", "Markets": ""}

    for section in sections:
        if section.startswith("Offices:"):
            info["Offices"] = section.replace("Offices:", "").strip()
        elif section.startswith("Stages:"):
            info["Stages"] = section.replace("Stages:", "").strip()
        elif section.startswith("Markets:"):
            info["Markets"] = section.replace("Markets:", "").strip()

    entries.append(info)

# Save to CSV
with open("../cleanedData/CLEAN_projectstartups.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Firm", "Offices", "Stages", "Markets"])
    writer.writeheader()
    for row in entries:
        writer.writerow(row)