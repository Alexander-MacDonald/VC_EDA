import json
import re
import pandas as pd

def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format in the file"

def extract_money_values(text):
    original_text = text
    normalized_text = text.lower()

    # Normalize en-dash, em-dash, and weird encoding like "â€“"
    normalized_text = re.sub(r'[–—â€“]', '-', normalized_text)

    # Match money patterns
    currency_symbols = r'[$€£¥]'
    money_pattern = rf'{currency_symbols}?\s*\d[\d,]*(?:\.\d+)?(?:\s?(?:k|m|b|thousand|million|billion))?'

    # Extract matches
    raw_money_matches = re.findall(money_pattern, normalized_text)
    cleaned_money_matches = [re.sub(r'\s+', '', m) for m in raw_money_matches if m.strip()]

    # Remove monetary values from the original text (case-insensitive)
    cleaned_text = original_text
    for raw in raw_money_matches:
        pattern = re.compile(re.escape(raw), re.IGNORECASE)
        cleaned_text = pattern.sub('', cleaned_text)

    # Normalize dashes again in cleaned text
    cleaned_text = re.sub(r'[–—â€“]', '-', cleaned_text)

    normalized_money_values = [
        val for m in cleaned_money_matches
        if (val := normalize_money(m)) is not None and val > 1000
    ]

    return normalized_money_values
    
def normalize_money(value):
    value = value.lower().replace('$', '').replace('€', '').replace('£', '').replace('¥', '')
    value = value.replace(',', '').strip()

    multiplier = 1
    if value.endswith('k'):
        multiplier = 1_000
        value = value[:-1]
    elif value.endswith('m'):
        multiplier = 1_000_000
        value = value[:-1]
    elif value.endswith('b'):
        multiplier = 1_000_000_000
        value = value[:-1]
    elif 'thousand' in value:
        multiplier = 1_000
        value = value.replace('thousand', '')
    elif 'million' in value:
        multiplier = 1_000_000
        value = value.replace('million', '')
    elif 'billion' in value:
        multiplier = 1_000_000_000
        value = value.replace('billion', '')

    try:
        return float(value.strip()) * multiplier
    except ValueError:
        return None

def buildCBDF(CBDatapoints):
    # Construct the dataframe from the list of CBDatapoint objects
    df = pd.DataFrame([{
        "index": dp.index,
        "firmname": dp.firmname,
        "concrete_value": dp.concreteValue,
        "unknown_value": dp.unknownValue,
        "total_potential": dp.concreteValue * dp.unknownValue,
        "check_context": dp.checkSizeContext,
        "MRR_context": dp.MRRContext,
        "founder_bias": dp.founderBias,
        "raw_data": dp.data
    } for dp in CBDatapoints])

    # Set the index of the DataFrame to the "index" column
    df.set_index("index", inplace=True)
    
    return df