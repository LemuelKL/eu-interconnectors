import os
import logging
from dataclasses import dataclass
import pandas as pd
import matplotlib.pyplot as plt
from client import Client

logging.basicConfig(level=logging.INFO)


BASE_DATA_DIR = "./../data"
FLOW_DATA_DIR = f"{BASE_DATA_DIR}/flow"
DAP_DATA_DIR = f"{BASE_DATA_DIR}/dap"
GENPPT_DATA_DIR = f"{BASE_DATA_DIR}/genppt"
for dir in [BASE_DATA_DIR, FLOW_DATA_DIR, DAP_DATA_DIR, GENPPT_DATA_DIR]:
    if not os.path.exists(dir):
        os.makedirs(dir)


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
logging.info(f"Found {len(interconnectors)} interconnectors in config.")

client = Client()

# Get physical flows for each interconnector
for idx, interconnector in interconnectors.iterrows():
    settings = {
        "in_domain": interconnector.in_domain,
        "out_domain": interconnector.out_domain,
        "start": global_start,
        "end": global_end,
    }
    df = client.qPhysicalFlows(**settings)
    df.to_csv(
        f"{FLOW_DATA_DIR}/{interconnector.in_country}_{interconnector.out_country}_{settings['start']}-{settings['end']}.csv"
    )
