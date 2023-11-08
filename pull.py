# Read in the security token from environment variable
import pandas as pd
import os
from dotenv import load_dotenv
import requests
import xmltodict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

load_dotenv()

securityToken = os.getenv("ENTSOE_TOKEN")
if securityToken is None:
    print("No security token found. Please set the environment variable `ENTSOE_TOKEN`")
    exit(1)
basePath = "https://web-api.tp.entsoe.eu/api?securityToken=" + securityToken

optionDict = {
    "documentType": "A11",
    "in_Domain": "10YGB----------A",
    "out_Domain": "10YFR-RTE------C",
    "periodStart": "201910312300",
    "periodEnd": "201911302300"
}

url = basePath + "&" + "&".join([key + "=" + optionDict[key] for key in optionDict])
print(url)
response = requests.get(url)
print(response.status_code)
respText = response.text
with open("response.xml", "w") as f:
    f.write(respText)

# Parse response XML into a dictionary
respDict = xmltodict.parse(respText)

# Print out the XML dictionary as a tree of keys and values
def printDict(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            printDict(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))

# printDict(respDict)
# print(respDict['Publication_MarketDocument']['TimeSeries'][0]['Period']['Point'])

timeseriesDatas = respDict['Publication_MarketDocument']['TimeSeries']
print(len(timeseriesDatas))

df = pd.DataFrame(columns=['position', 'quantity'])
for timeseriesData in timeseriesDatas:
    df = pd.concat([df, pd.DataFrame(timeseriesData['Period']['Point'])], ignore_index=True)
print(df)
print(df.describe())

# Plot the data
df['quantity'] = pd.to_numeric(df['quantity'])
df['quantity'].plot()
plt.show()





