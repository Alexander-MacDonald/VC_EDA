import re
from CButils import *
from CBdatapoint import *
pd.set_option('display.max_colwidth', 0)

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
#if check size in range (isolate numbers from text, only reliable way) - done
#   no isolatable numbers? add to missing value - done
#add mrr nuance - done

#DONE ADD POTENTIAL SCORE

#easily tokenable items
country_tokens = set()
investment_stage_tokens = set()
industries_tokens = set()
geographic_focus_tokens = set()

#companies that are erroneous
keyErrors = []
#companies that invest in b2b, ai, and hardware
goalEntries = []

#output data
processedData = []

file_path = 'output/chatgpt4.json'
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

    #check size logic based on CBdatapoints.py
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
                #removing error values below 1000 will make this potentially an "up to" category now, tokenization can be messy
                if(LARGE_CHECK < rangevalues[0]):
                    firm.updateWeight("up_to_check")
                    firm.addCheckSizeContext("Below Up To Max")
                else:
                    firm.updateWeight("out_of_range_check")
                    firm.addCheckSizeContext("Out of Check Range")
            else:
                if(LARGE_CHECK < rangevalues[0] or SMALL_CHECK > rangevalues[1]):
                    firm.updateWeight("out_of_range_check")
                    firm.addCheckSizeContext("Out of Check Range")
                else:
                    firm.updateWeight("in_range_check")
                    firm.addCheckSizeContext("In Funding Range")

        elif("up to" in checksize):
            #checks described with only an upper limit
            if(LARGE_CHECK < rangevalues[0]):
                firm.updateWeight("up_to_check")
                firm.addCheckSizeContext("Below Up To Max")
            else:                    
                firm.updateWeight("out_of_range_check")
                firm.addCheckSizeContext("Out of Check Range")
        elif("needs" in checksize or "varies" in checksize or "vary" in checksize):
            #gpt response regarding vagueness "business needs"
            firm.updateUnknownWeight("potential_check")
            firm.addCheckSizeContext("Varies")
        elif("disclosed" in checksize or "not publicly" in checksize):
            #gpt response regarding undisclosed checks
            firm.updateUnknownWeight("potential_check")
            firm.addCheckSizeContext("Not Disclosed")
        elif("n/a" in checksize or checksize == ""):
            #gpt response for missing data
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
            firm.addMRRContext("Pre-Revenue")
        elif("traction" in mrr):
            #traction was often used to say early stage companies with some revenue, our current MRR is 0, can be updated in CBdatapoint.py
            if(CURRENT_MRR == 0):
                firm.updateWeight("out_of_mrr_range")
                firm.addMRRContext("MRR Out of Range")
            else:
                firm.updateWeight("in_mrr_range")
                firm.addMRRContext("In MRR Range")
        elif("varies" in mrr or "vary" in mrr or "not specified" in mrr):
            firm.updateUnknownWeight("no_mrr_data")
            firm.addMRRContext("Variable Requirements")
        else:
            potential_numbers = extract_money_values(mrr)
            if(len(potential_numbers) > 0):
                if(potential_numbers[0] > CURRENT_MRR):
                    firm.updateWeight("out_of_mrr_range")
                    firm.addMRRContext("MRR Out of Range")
                else:
                    firm.updateWeight("in_mrr_range")
                    firm.addMRRContext("In MRR Range")
            else:
                firm.updateUnknownWeight("no_mrr_data")
                firm.addMRRContext("Specific MRR Classifier")

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
    
    #ai industry regex - avoided cases where "sustAInability" was being caught
    ai_pattern = re.compile(r'\b(ai|gen ai|artificial intelligence)\b', re.IGNORECASE)

    if(entry["industries"] != None):
        if(any(ai_pattern.search(industry) for industry in entry["industries"])):
            firm.updateWeight("ai_industry")

        if(any("hardware" in industry.lower() for industry in entry["industries"])):
            firm.updateWeight("hardware_industry")

        if(any("space" in industry.lower() for industry in entry["industries"])):
            firm.updateWeight("space_industry")
    else:
        firm.updateUnknownWeight("ai_industry")
        firm.updateUnknownWeight("hardware_industry")


    if(entry["geographic_focus"] != None):
        #if we hallucinate non string datatype
        if(type(entry["geographic_focus"]) is not str):
            print("TYPE ERROR: ", type(entry["geographic_focus"]))

        if("global" in entry["geographic_focus"].lower()):
            firm.updateWeight("global_focus")

        elif("united states" in entry["geographic_focus"].lower() or " usa " in entry["geographic_focus"].lower()):
            firm.updateWeight("us_focus")
            #geographic terms found in the initial 3k company data set
            #they are specified in CBdatapoint.py
            if(any(keyword in entry["geographic_focus"] for keyword in INCLUDED_US_REGION_TOKENS)):
                firm.updateWeight("us_region_focus")
    else:
        firm.updateUnknownWeight("global_focus")
        firm.updateUnknownWeight("us_focus")

    firm.addFounderBias(entry["founder_profile_bias"])
    processedData.append(firm)

print("NUMBER OF FIRMS: " + str(len(json_data)))
print("NUMBER OF JSON KEY ERRORS: " + str(len(keyErrors)) + "\n")
print("NUMBER OF DATA POINTS: ", len(processedData))

df = buildCBDF(processedData)
df_sorted = df.sort_values(by="concrete_value", ascending=False)
df_sorted.head(50).to_csv("VC_REPORT.csv", index=False)
print(df_sorted.drop(columns=["raw_data", "founder_bias"]).head(20).to_string())
print(calculateDataPointCount(json_data))

#collect all tokens
# for hat_trick_firm in goalEntries:

#     country_tokens.add(hat_trick_firm["country"].lower())
#     for stage in hat_trick_firm["investment_stage_focus"]:
#         investment_stage_tokens.add(stage.lower())
#     for industry in hat_trick_firm["industries"]:
#         industries_tokens.add(industry.lower())
#     geographic_focus_tokens.add(hat_trick_firm["geographic_focus"].lower())


