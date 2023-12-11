import logging
from dotenv import load_dotenv
import os
import requests
import xmltodict
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


RESOLUTION_TABLE = {
    "PT15M": "15min",
    "PT30M": "30min",
    "PT60M": "60min",
    "P1D": "1day",
    "P7D": "1week",
    "P1M": "1month",
    "P1Y": "1year",
}

PsrType = pd.read_csv("psrtype.csv")


class Client:
    def __init__(self):
        load_dotenv()
        securityToken = os.getenv("ENTSOE_TOKEN")
        if securityToken is None:
            logger.error(
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
        # Check if request date range exceeds 1 year
        start = pd.to_datetime(optionDict["periodStart"])
        end = pd.to_datetime(optionDict["periodEnd"])

        # Break into 1 year chunks
        resp_dicts = []

        while start < end:
            if (end - start).days > 365:
                url = self.get_request_url(
                    {
                        **optionDict,
                        "periodStart": start.strftime("%Y%m%d0000"),
                        "periodEnd": (start + pd.DateOffset(days=365)).strftime(
                            "%Y%m%d0000"
                        ),
                    }
                )
                start = start + pd.DateOffset(days=365)
            else:
                url = self.get_request_url(
                    {
                        **optionDict,
                        "periodStart": start.strftime("%Y%m%d0000"),
                        "periodEnd": end.strftime("%Y%m%d0000"),
                    }
                )
                start = end

            logger.info(f"{url}")
            response = requests.get(url)
            if response.status_code != 200:
                logger.error(response.status_code)
                logger.error(response.text)
                exit(1)
            respText = response.text
            respDict = xmltodict.parse(respText)
            resp_dicts.append(respDict)

        return resp_dicts

    def print_dict(self, d, indent=0):
        for key, value in d.items():
            print("\t" * indent + str(key))
            if isinstance(value, dict):
                self.print_dict(value, indent + 1)
            else:
                print("\t" * (indent + 1) + str(value))

    def process_publication_market_document(self, document, col_name):
        TimeSeries = document["TimeSeries"]
        if isinstance(TimeSeries, list):
            timeseries_datas = TimeSeries
        else:
            timeseries_datas = [TimeSeries]

        df = pd.DataFrame(columns=[col_name])

        for timeseries_data in timeseries_datas:
            period = timeseries_data["Period"]
            time_interval_start = period["timeInterval"]["start"]
            time_interval_end = period["timeInterval"]["end"]
            resolution = period["resolution"]
            assert resolution in RESOLUTION_TABLE
            logger.info(f"{time_interval_start} {time_interval_end} {resolution}")
            data_points = period["Point"]
            time_counter = pd.date_range(
                start=time_interval_start,
                end=time_interval_end,
                freq=RESOLUTION_TABLE[resolution],
            )
            for data_point in data_points:
                df = pd.concat(
                    [
                        df if not df.empty else None,
                        pd.DataFrame(
                            {
                                col_name: data_point[col_name],
                            },
                            index=[
                                time_counter[int(data_point["position"]) - 1]
                            ],  # position starts at 1
                        ),
                    ],
                )

        df[col_name] = pd.to_numeric(df[col_name])
        return df

    def process_gl_market_document(self, document, col_name):
        TimeSeries = document["TimeSeries"]
        if isinstance(TimeSeries, list):
            timeseries_datas = TimeSeries
        else:
            timeseries_datas = [TimeSeries]

        dfs = {}
        for timeseries_data in timeseries_datas:
            production_type = timeseries_data["MktPSRType"]["psrType"]
            period = timeseries_data["Period"]
            time_interval_start = period["timeInterval"]["start"]
            time_interval_end = period["timeInterval"]["end"]
            resolution = period["resolution"]
            assert resolution in RESOLUTION_TABLE
            logger.info(f"{time_interval_start} {time_interval_end} {resolution}")
            data_points = period["Point"]
            time_counter = pd.date_range(
                start=time_interval_start,
                end=time_interval_end,
                freq=RESOLUTION_TABLE[resolution],
            )
            for data_point in data_points:
                df = pd.DataFrame(
                    {
                        production_type: data_point[col_name],
                    },
                    index=[
                        time_counter[int(data_point["position"]) - 1]
                    ],  # position starts at 1
                )

                if production_type not in dfs:
                    dfs[production_type] = df
                else:
                    dfs[production_type] = pd.concat(
                        [dfs[production_type], df],
                    )

        for production_type in dfs:
            dfs[production_type] = pd.to_numeric(dfs[production_type][production_type])
        df = pd.concat(dfs.values(), axis=1, keys=dfs.keys())
        df.columns = df.columns.map(PsrType.set_index("Code")["Meaning"].to_dict())
        df = df.reindex(sorted(df.columns), axis=1)
        return df

    # 4.2.15. Physical Flows [12.1.G]
    # https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#:~:text=4.2.15.%20Physical%20Flows%20%5B12.1.G%5D
    def qPhysicalFlows(self, in_domain, out_domain, start, end):
        resp_dicts = self.query_api(
            {
                "documentType": "A11",
                "in_Domain": in_domain,
                "out_Domain": out_domain,
                "periodStart": start,
                "periodEnd": end,
            }
        )
        df = pd.DataFrame(columns=["quantity"])
        for resp_dict in resp_dicts:
            if "Publication_MarketDocument" not in resp_dict:
                continue
            df = pd.concat(
                [
                    df if not df.empty else None,
                    self.process_publication_market_document(
                        resp_dict["Publication_MarketDocument"], "quantity"
                    ),
                ]
            )
        return df

    # 4.2.10. Day Ahead Prices [12.1.D]
    # https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#:~:text=4.2.10.%20Day%20Ahead%20Prices%20%5B12.1.D%5D
    def qDayAheadPrices(self, domain, start, end):
        resp_dicts = self.query_api(
            {
                "documentType": "A44",
                "in_Domain": domain,
                "out_Domain": domain,
                "periodStart": start,
                "periodEnd": end,
            }
        )
        df = pd.DataFrame(columns=["price.amount"])
        for resp_dict in resp_dicts:
            if "Publication_MarketDocument" not in resp_dict:
                continue
            df = pd.concat(
                [
                    df if not df.empty else None,
                    self.process_publication_market_document(
                        resp_dict["Publication_MarketDocument"], "price.amount"
                    ),
                ]
            )
        return df

    def qActualGenerationPerProductionType(self, domain, start, end):
        resp_dicts = self.query_api(
            {
                "documentType": "A75",
                "processType": "A16",
                "in_Domain": domain,
                "periodStart": start,
                "periodEnd": end,
            }
        )
        df = pd.DataFrame()
        for resp_dict in resp_dicts:
            if "GL_MarketDocument" not in resp_dict:
                continue
            df = pd.concat(
                [
                    df if not df.empty else None,
                    self.process_gl_market_document(
                        resp_dict["GL_MarketDocument"], "quantity"
                    ),
                ]
            )
        return df
