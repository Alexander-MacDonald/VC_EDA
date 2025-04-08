import csv

stage_keywords = {"Pre-Seed", "Seed", "Series A", "Series B+", "Series B", "Series C", "Series D"}

entries = []
current_block = []

def is_noise(line):
    noise_keywords = [
        "VC Resource", "Browse Harmonic", "Learn more about Harmonic", "Partner"
    ]
    return any(n in line for n in noise_keywords)

def flush_block(block):
    if not block or len(block) < 2:
        return None

    firm = block[0]
    stage_lines = []
    description_lines = []

    for line in block[1:]:
        if line.strip() in stage_keywords:
            stage_lines.append(line.strip())
        else:
            description_lines.append(line.strip())

    return {
        "Firm": firm.strip(),
        "Description": " ".join(description_lines).strip(),
        "Stages": ", ".join(stage_lines)
    }

with open("../data/vcsheet.com.txt", "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if not line or is_noise(line):
            continue

        if line == "Website":
            parsed = flush_block(current_block)
            if parsed:
                entries.append(parsed)
            current_block = []
        else:
            current_block.append(line)

# Write to CSV
with open("../cleanedData/CLEAN_vcsheet.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Firm", "Description", "Stages"])
    writer.writeheader()
    writer.writerows(entries)
