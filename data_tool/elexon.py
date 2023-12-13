import pandas as pd

# Special handling for UK data from ELEXON
uk_df = pd.read_csv(
    "./../data/InterconnectorFlows-2016-01-01T00_00_00.000Z-2023-12-12T09_30_00.000Z.csv",
)
uk_df = uk_df[
    ["StartTime", "SettlementDate", "SettlementPeriod", "FuelType", "Generation"]
]

# Explot rows into columns
uk_df = uk_df.pivot_table(
    index=["SettlementDate", "SettlementPeriod"],
    columns="FuelType",
    values="Generation",
)
# Drop "FuelType" column
uk_df = uk_df.reset_index()
# Keep only interconnectors
ics = [col for col in list(uk_df.columns) if col[:3] == "INT"]
uk_df = uk_df[["SettlementDate", "SettlementPeriod"] + ics]
