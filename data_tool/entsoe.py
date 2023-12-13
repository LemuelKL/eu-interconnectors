import os
import logging
from dataclasses import dataclass
import pandas as pd
import matplotlib.pyplot as plt
from client import Client

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


client = Client()
# Settings
global_start = "202304010000"
global_end = "202311010000"
area_df = pd.read_csv("area.csv")


def lookup_domain_code(key):
    return area_df[area_df["Key"] == key]["Code"].iloc[0]


def download_flow_data():
    config = pd.read_csv("config_physical_flow_cty.csv")
    logging.info(f"Found {len(config)} interconnectors in config.")

    # Get physical flows between each pair of countries
    for idx, interconnector in config.iterrows():
        from_cty = interconnector.from_cty
        from_cty_abbrv = from_cty[from_cty.find("(") + 1 : from_cty.find(")")]
        to_cty = interconnector.to_cty
        to_cty_abbrv = to_cty[to_cty.find("(") + 1 : to_cty.find(")")]

        file_name = f"{FLOW_DATA_DIR}/{from_cty_abbrv}_{to_cty_abbrv}_{global_start}-{global_end}.csv"
        # Check if file already exists
        if os.path.exists(file_name):
            logging.info(f"Skipping {from_cty} -> {to_cty} as file already exists.")
            continue

        out_domain = lookup_domain_code(from_cty)
        in_domain = lookup_domain_code(to_cty)

        settings = {
            "in_domain": in_domain,
            "out_domain": out_domain,
            "start": global_start,
            "end": global_end,
        }
        df = client.qPhysicalFlows(**settings)
        df.to_csv(file_name)
        logging.info(f"Saved {from_cty} -> {to_cty} to {file_name}")


def download_price_data():
    # Read cty from file
    bzns = pd.read_csv("config_day_ahead_price.csv")
    logging.info(f"Found {len(bzns)} bidding zones in config.")

    for idx, bzn in bzns.iterrows():
        bzn = bzn.bzn
        domain = lookup_domain_code(bzn)
        file_name = f"{DAP_DATA_DIR}/{bzn[4:]}_{global_start}-{global_end}.csv"
        # Check if file already exists
        if os.path.exists(file_name):
            logging.info(f"Skipping {bzn} as file already exists.")
            continue

        settings = {
            "domain": domain,
            "start": global_start,
            "end": global_end,
        }
        df = client.qDayAheadPrices(**settings)
        df.to_csv(file_name)
        logging.info(f"Saved {bzn} to {file_name}")


if __name__ == "__main__":
    download_flow_data()
    # download_price_data()
