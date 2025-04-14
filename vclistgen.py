import pandas as pd

df = pd.read_csv('vc_data_dump.csv')

promptdf = df["Firm"].apply(lambda x: "Using provided JSON format: " + x)

df["Firm"].to_csv('list.csv', index = False)
promptdf.to_csv('promptlist.csv', index = False)
