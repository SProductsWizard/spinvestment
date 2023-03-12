import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd

from pymongo import MongoClient
from DatabaseManagement.config import DBConfigDict


class AtlasDriver:
    def __init__(self, readOnly=False):
        if readOnly:
            self.client = MongoClient(DBConfigDict["Atlas"]["endpointReadonly"])
        else:
            self.client = MongoClient(DBConfigDict["Atlas"]["endpoint"])

        self.database = self.client[DBConfigDict["Atlas"]["database"]]

    def setCol(self, colName):
        self.col = self.database[colName]

    def load_data(self, colName):
        col = self.database[colName]
        dataPull = pd.DataFrame(
            list(
                col.find(
                    {},
                    {
                        "_id": 0,
                    },
                )
            )
        )
        return dataPull

    # def delete_data(self, cutDate):
    #     cutDate = pd.to_datetime(cutDate)
    #     col = self.database["FinsightNIBond"]
    #     x = col.delete_many(
    #         {"$expr": {"$gte": [{"$toDate": "$PRICING DATE"}, cutDate]}}
    #     )

    #     print(f"deleted records since: {cutDate}")
    #     print(f"deleted records: {x.deleted_count}")

    #     return

    def upload_data_NIBond(self, df):
        df = df.drop(["Unnamed: 0", "Price"], axis=1)
        df = df.rename(columns={"Unnamed: 22": "PRICE"})

        df["Pricing Date"] = pd.to_datetime(df["Pricing Date"])
        df["Ticker"] = df["Ticker"].str.strip()
        df["Series"] = df["Series"].str.strip()
        df["Deal Name"] = df["Ticker"] + " " + df["Series"]
        df["Sector"] = "ABS"
        df = df.rename(
            columns={
                "Pricing Date": "PRICING DATE",
                "Sector": "SECTOR",
                "Region": "REGION",
                "Ticker": "TICKER",
                "Series": "SERIES",
            }
        )

        dbDf = self.load_data(colName="FinsightNIBond")
        df = df[~df["Deal Name"].isin(dbDf["Deal Name"])]

        self.database["FinsightNIBond"].insert_many(df.to_dict("records"))

        return self

    def upload_data_NIDeal(self, df):
        dbDf = self.load_data(colName="FinsightNIDeal")
        dbDf["Deal Name"] = dbDf["Deal Name"].str.strip()
        df = df[~df["Deal Name"].isin(dbDf["Deal Name"])]
        self.database["FinsightNIDeal"].insert_many(df.to_dict("records"))

        return self
