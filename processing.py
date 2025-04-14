import re
from CButils import *
from CBdatapoint import *

#score methodology
#if invests in b2b - done
#if invests in ai - done
#if invests in hardware - done
#if in US - done
#if stage contains seed - done
#if geographic focus in us/united states #TODO: ADD NUANCE FOR REGIONS
#if geographic focus in global
#if hardware subtring listed in industry - done
#if ai substring listed in industry - done
#if check size in range (isolate numbers from text, only reliable way)
#   no isolatable numbers? add to missing value
#add mrr nuance

#TODO ADD POTENTIAL SCORE

#easily tokenable items
country_tokens = set()
investment_stage_tokens = set()
industries_tokens = set()
geographic_focus_tokens = set()

keyErrors = []
goalEntries = []

processedData = []

file_path = 'chatgpt4.json'
json_data = read_json_file(file_path)

for idx, entry in enumerate(json_data):
    #removing bad data
    if("invests_in_hardware_companies" not in entry.keys() or entry["entry_malformed"] or entry["is_angel_investor"]):
        keyErrors.append(entry)
        continue

    if("firm_name" not in entry.keys()):
        keyErrors.append(entry)
        continue

    firm = CBDatapoint(idx, entry["firm_name"], 1, 1, entry)

    #for easy tracking of tokens in targeted companies
    if(entry["invests_in_ai_companies"] and entry["invests_in_hardware_companies"] and entry["invests_in_b2b_companies"]):
        goalEntries.append(entry)

    if(entry["estimated_check_size_text"] != None):
        checksize = entry["estimated_check_size_text"].lower()
        rangevalues = extract_money_values(checksize)
        if(len(rangevalues) == 0):
            firm.updateUnknownWeight("potential_check")
        elif("between" in checksize or "from" in checksize or "â€“" in checksize or "range" in checksize or "to" in checksize):
            #out of investment range
            #check if large_check < range min
            #check if small_check > range max
            if(len(rangevalues) == 1):
                if(LARGE_CHECK < rangevalues[0]):
                    firm.updateWeight("up_to_check")
                else:
                    firm.updateWeight("out_of_range_check")
            else:
                if(LARGE_CHECK < rangevalues[0] or SMALL_CHECK > rangevalues[1]):
                    firm.updateWeight("out_of_range_check")
                else:
                    firm.updateWeight("in_range_check")

        elif("up to" in checksize):
            if(LARGE_CHECK < rangevalues[0]):
                firm.updateWeight("up_to_check")
            else:                    
                firm.updateWeight("out_of_range_check")
        elif("needs" in checksize or "varies" in checksize or "vary" in checksize):
            firm.updateUnknownWeight("potential_check")
            firm.addCheckSizeContext("Varies")
        elif("disclosed" in checksize or "not publicly" in checksize):
            firm.updateUnknownWeight("potential_check")
            firm.addCheckSizeContext("Not Disclosed")
        elif("n/a" in checksize or checksize == ""):
            firm.updateUnknownWeight("potential_check")
            firm.addCheckSizeContext("No Data")
        else:
            firm.updateUnknownWeight("potential_check")
            firm.addCheckSizeContext("No Data")
    else:
        firm.updateUnknownWeight("potential_check")
        firm.addCheckSizeContext("No Data")

    mrr = entry["monthly_recurring_revenue_range"]
    if(mrr == None or mrr == ""):
        firm.updateUnknownWeight("no_mrr_data")
        firm.addMRRContext("No Data")
    else:
        mrr = mrr.lower()
        if("pre-revenue" in mrr or "$0" in mrr):
            firm.updateWeight("pre_revenue")
        elif("traction" in mrr):
            if(CURRENT_MRR == 0):
                firm.updateWeight("out_of_mrr_range")
            else:
                firm.updateWeight("in_mrr_range")
        elif("varies" in mrr or "vary" in mrr or "not specified" in mrr):
            firm.updateUnknownWeight("no_mrr_data")
            firm.addMRRContext("Variable Requirements")
        else:
            potential_numbers = extract_money_values(mrr)
            if(len(potential_numbers) > 0):
                if(potential_numbers[0] > CURRENT_MRR):
                    firm.updateWeight("out_of_mrr_range")
                else:
                    firm.updateWeight("in_mrr_range")
            else:
                firm.updateUnknownWeight("no_mrr_data")
                firm.addMRRContext("Specific Classifier")

    if(entry["invests_in_hardware_companies"]):
        firm.updateWeight("invests_in_hardware")
    if(entry["invests_in_b2b_companies"]):
        firm.updateWeight("invests_in_b2b")
    if(entry["invests_in_ai_companies"]):
        firm.updateWeight("invests_in_ai")

    if(entry["country"] != None):
        if(entry["country"].lower() == "united states"):
            firm.updateWeight("us_based")
    else:
        firm.updateUnknownWeight("us_based")

    if(entry["investment_stage_focus"] != None):
        if(any("seed" in stage.lower() for stage in entry["investment_stage_focus"])):
            firm.updateWeight("seed_stage")
    else:
        firm.updateUnknownWeight("seed_stage")
    
    #ai regex
    ai_pattern = re.compile(r'\b(ai|gen ai|artificial intelligence)\b', re.IGNORECASE)

    if(entry["industries"] != None):
        if(any(ai_pattern.search(industry) for industry in entry["industries"])):
            firm.updateWeight("ai_industry")

        if(any("hardware" in industry.lower() for industry in entry["industries"])):
            firm.updateWeight("hardware_industry")
    else:
        firm.updateUnknownWeight("ai_industry")
        firm.updateUnknownWeight("hardware_industry")

    if(entry["geographic_focus"] != None):
        if(any("global" in sector.lower() for sector in entry["geographic_focus"])):
            firm.updateWeight("global_focus")

        if(any("united states" in sector.lower() for sector in entry["geographic_focus"])):
            firm.updateWeight("us_focus")
        
        if(any(" usa " in sector.lower() for sector in entry["geographic_focus"])):
            firm.updateWeight("us_focus")
    else:
        firm.updateUnknownWeight("global_focus")
        firm.updateUnknownWeight("us_focus")

    processedData.append(firm)

print("NUMBER OF FIRMS: " + str(len(json_data)))
print("NUMBER OF JSON KEY ERRORS: " + str(len(keyErrors)) + "\n")
print("NUMBER OF DATA POINTS: ", len(processedData))

df = buildCBDF(processedData)
df_sorted = df.sort_values(by="concrete_value", ascending=False)
print(df_sorted.head(20).to_string())

#collect all tokens
# for hat_trick_firm in goalEntries:

#     country_tokens.add(hat_trick_firm["country"].lower())
#     for stage in hat_trick_firm["investment_stage_focus"]:
#         investment_stage_tokens.add(stage.lower())
#     for industry in hat_trick_firm["industries"]:
#         industries_tokens.add(industry.lower())
#     geographic_focus_tokens.add(hat_trick_firm["geographic_focus"].lower())


