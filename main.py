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
df = client.qPhysicalFlows(
    in_domain="10YGB----------A",
    out_domain="10YFR-RTE------C",
    start="201810310000",
    end="201811070000",
)
df.to_csv("data_physical_flows.csv")
df = client.qDayAheadPrices(
    domain="10YNL----------L",
    start="201810310000",
    end="201811070000",
)
df.to_csv("data_day_ahead_prices.csv")
