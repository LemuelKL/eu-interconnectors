from dotenv import load_dotenv
import os
import requests
import xmltodict
import pandas as pd


RESOLUTION_TABLE = {
    "PT15M": "15min",
    "PT30M": "30min",
    "PT60M": "60min",
    "P1D": "1day",
    "P7D": "1week",
    "P1M": "1month",
    "P1Y": "1year",
}


class Client:
    def __init__(self):
        load_dotenv()
        securityToken = os.getenv("ENTSOE_TOKEN")
        if securityToken is None:
            print(
                "No security token found. Please set the environment variable `ENTSOE_TOKEN`"
            )
            exit(1)
        self.basePath = (
            "https://web-api.tp.entsoe.eu/api?securityToken=" + securityToken
        )

    def get_request_url(self, optionDict):
        return (
            self.basePath
            + "&"
            + "&".join([key + "=" + optionDict[key] for key in optionDict])
        )

    def query_api(self, optionDict):
        url = self.get_request_url(optionDict)
        response = requests.get(url)
        print(response.status_code)
        respText = response.text
        with open("response.xml", "w") as f:
            f.write(respText)
        respDict = xmltodict.parse(respText)
        return respDict

    def print_dict(self, d, indent=0):
        for key, value in d.items():
            print("\t" * indent + str(key))
            if isinstance(value, dict):
                self.print_dict(value, indent + 1)
            else:
                print("\t" * (indent + 1) + str(value))

    # 4.2.15. Physical Flows [12.1.G]
    # https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#:~:text=4.2.15.%20Physical%20Flows%20%5B12.1.G%5D
    def qPhysicalFlows(self, in_domain, out_domain, start, end):
        # optionDict = {
        #     "documentType": "A11",
        #     "in_Domain": "10YGB----------A",
        #     "out_Domain": "10YFR-RTE------C",
        #     "periodStart": "201810310000",
        #     "periodEnd": "201811070000",
        # }
        respDict = self.query_api(
            {
                "documentType": "A11",
                "in_Domain": in_domain,
                "out_Domain": out_domain,
                "periodStart": start,
                "periodEnd": end,
            }
        )

        timeseriesDatas = [] + [
            respDict["Publication_MarketDocument"]["TimeSeries"]
        ]  # this is a hack to explicitly create a list

        df = pd.DataFrame(columns=["quantity"])
        for timeseriesData in timeseriesDatas:
            time_interval_start = timeseriesData["Period"]["timeInterval"]["start"]
            time_interval_end = timeseriesData["Period"]["timeInterval"]["end"]
            resolution = timeseriesData["Period"]["resolution"]
            assert resolution in RESOLUTION_TABLE
            print(time_interval_start, time_interval_end, resolution)
            data_points = timeseriesData["Period"]["Point"]
            time_counter = pd.date_range(
                start=time_interval_start,
                end=time_interval_end,
                freq=RESOLUTION_TABLE[resolution],
            )
            for data_point in data_points:
                df = pd.concat(
                    [
                        df,
                        pd.DataFrame(
                            {
                                "quantity": data_point["quantity"],
                            },
                            index=[
                                time_counter[int(data_point["position"]) - 1]
                            ],  # position starts at 1
                        ),
                    ],
                )

        df["quantity"] = pd.to_numeric(df["quantity"])
        return df
