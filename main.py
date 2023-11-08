import pandas as pd
import matplotlib.pyplot as plt
from client import Client

client = Client()
df = client.qPhysicalFlows(
    in_domain="10YGB----------A",
    out_domain="10YFR-RTE------C",
    start="201810310000",
    end="201811070000",
)

print(df.head())
