from dataclasses import dataclass
import pandas as pd
import matplotlib.pyplot as plt
from client import Client

# BZN — Bidding Zone
# BZA — Bidding Zone Aggregation
# CTA — Control Area
# MBA — Market Balance Area
# IBA — Imbalance Area
# IPA — Imbalance Price Area
# LFA — Load Frequency Control Area
# LFB — Load Frequency Control Block
# REG — Region
# SCA — Scheduling Area
# SNA — Synchronous Area

# 10YGB----------A
# LFA|GB, LFB|GB, SNA|GB, MBA|GB, SCA|GB, CTA|National Grid, BZN|GB

# 10YFR-RTE------C
# BZN|FR, France (FR), CTA|FR, SCA|FR, MBA|FR, LFB|FR, LFA|FR

# 10YNL----------L
# LFA|NL, LFB|NL, CTA|NL, Netherlands (NL), BZN|NL, SCA|NL, MBA|NL

client = Client()
# df = client.qPhysicalFlows(
#     in_domain="10YGB----------A",
#     out_domain="10YFR-RTE------C",
#     start="201810310000",
#     end="201811070000",
# )
# df.to_csv("data_physical_flows.csv")


@dataclass
class Interconnector:
    country: str
    in_domain: str
    out_domain: str

    def __repr__(self):
        return f"{self.country} {self.in_domain} {self.out_domain}"


# Read interconnectors from file
interconnectors = pd.read_csv("interconnector_config.csv")
print(interconnectors)

# Get physical flows for each interconnector
for idx, interconnector in interconnectors.iterrows():
    settings = {
        "in_domain": interconnector.in_domain,
        "out_domain": interconnector.out_domain,
        "start": "202301010000",
        "end": "202302010000",
    }
    df = client.qPhysicalFlows(**settings)
    df.to_csv(
        f"data_physical_flows__{interconnector.country}_{settings['in_domain']}_{settings['out_domain']}_{settings['start']}_{settings['end']}.csv"
    )

# df = client.qDayAheadPrices(
#     domain="10YNL----------L",
#     start="202301010000",
#     end="202310010000",
# )
# df.to_csv("data_day_ahead_prices.csv")
# # Plot
# df["day_moving_average"] = df["price"].rolling(window=24).mean()
# df.plot()
# plt.ylabel("Price (€/MWh)")
# plt.xlabel("Time")
# plt.title("Day Ahead Prices of Netherlands (NL)")
# plt.show()
