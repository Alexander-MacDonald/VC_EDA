SMALL_CHECK = 300_000
LARGE_CHECK = 750_000
CURRENT_MRR = 0

#tokens based on dataset, will change with more data
EXCLUDED_US_REGION_TOKENS = [
    "southeastern",
    "rocky mountain",
    "texas",
    "new york",
    "midwest",
    "middle america",
    "california",
    "west coast",
    "florida",
    "underserved",
    "southeast",
    "rockies",
    "southwest",
    "colorado",
    "pacific northwest",
    "mid-america",
]

INCLUDED_US_REGION_TOKENS = [
    "northeast",
    "east coast",
    "boston",
    "massachusetts",
    "eastern",
    " ma ",
]

WEIGHTS = {
    "invests_in_hardware" : 1.2,
    "invests_in_b2b" : 1.1,
    "invests_in_ai" : 1.1,
    "us_based" : 1.1,
    "seed_stage": 1.2,
    "ai_industry": 1.1,
    "hardware_industry": 1.2,
    "space_industry": 0.8,
    "global_focus": 1.1,
    "us_focus": 1.2,
    "out_of_range_check": 0.01,
    "in_range_check": 1.3,
    "up_to_check": 1.15,
    "potential_check": 1.05,
    "no_mrr_data": 1.1,
    "pre_revenue": 1.4,
    "in_mrr_range": 1.2,
    "out_of_mrr_range": 0.01,
    "us_region_focus": 1.1
}

class CBDatapoint:
    def __init__(self, index, firmname, concreteValue, unknownValue, rawdata):
        self.index = index
        self.firmname = firmname
        self.concreteValue = concreteValue
        self.unknownValue = unknownValue
        self.data = rawdata
        self.checkSizeContext = ""
        self.MRRContext = ""
        self.founderBias = ""
    
    def __str__(self):
        return f'{self.index} | {self.firmname} | {self.concreteValue} | {self.unknownValue}\n'

    def updateWeight(self, weightKey):
        self.concreteValue *= WEIGHTS[weightKey]

    def updateUnknownWeight(self, weightKey):
        self.unknownValue *= WEIGHTS[weightKey]

    def addCheckSizeContext(self, context):
        self.checkSizeContext = context

    def addMRRContext(self, context):
        self.MRRContext = context

    def addFounderBias(self, bias):
        self.founderBias = bias