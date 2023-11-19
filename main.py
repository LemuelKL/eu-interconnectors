import os
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

DATA_DIR = "data"
# Create data directory if not exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


@dataclass
class Interconnector:
    country: str
    in_domain: str
    out_domain: str

    def __repr__(self):
        return f"{self.country} {self.in_domain} {self.out_domain}"


# Settings
global_start = "202304010000"
global_end = "202311010000"

# Read interconnectors from file
interconnectors = pd.read_csv("config_physical_flow_cty.csv")
print(interconnectors)

# Get physical flows for each interconnector
for idx, interconnector in interconnectors.iterrows():
    settings = {
        "in_domain": interconnector.in_domain,
        "out_domain": interconnector.out_domain,
        "start": global_start,
        "end": global_end,
    }
    df = client.qPhysicalFlows(**settings)
    print(df)
    df.to_csv(
        f"{DATA_DIR}/physical_flow__{interconnector.country}_{settings['in_domain']}_{settings['out_domain']}_{settings['start']}_{settings['end']}.csv"
    )

df = client.qDayAheadPrices(
    domain="10YNL----------L",
    start=global_start,
    end=global_end,
)
print(df)
df.to_csv(
    f"{DATA_DIR}/day_ahead_price__10YNL----------L_{global_start}_{global_end}.csv"
)

df = client.qActualGenerationPerProductionType(
    domain="10YNL----------L", start=global_start, end=global_end
)
print(df)
df.to_csv(
    f"{DATA_DIR}/actual_generation_per_production_type__10YNL----------L_{global_start}_{global_end}.csv"
)
