import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from DatabaseManagement.db_driver import AtlasDriver


class SPCFdb_mgmt:
    def __init__(self):
        self.driver = AtlasDriver(readOnly=False)

    def load_assetRepline(self):
        df = self.driver.load_data(colName="SPCF_assetRepline")
        df = df[["replineIndex"] + [col for col in df.columns if col != "replineIndex"]]
        df = df.sort_values(by="replineIndex", ascending=True)
        return df

    def load_rampPool(self):
        df = self.driver.load_data(colName="SPCF_rampPool")
        df = df[["rampIndex"] + [col for col in df.columns if col != "rampIndex"]]
        df = df.sort_values(by="rampIndex", ascending=True)

        return df

    def upload_assetRepline(self, newReplineDf):
        self.driver.database["SPCF_assetRepline"].insert_many(
            newReplineDf.to_dict("records")
        )
        return self

    def finsightDataStatus(self):
        finsightAbbNIBond = self.driver.load_data("FinsightNIBond")[
            ["PRICING DATE", "Deal Name"]
        ]
        finsightAbbNIDeal = self.driver.load_data("FinsightNIDeal")[
            ["Pricing Date", "Deal Name"]
        ]

        maxPricingDateABSBond = finsightAbbNIBond["PRICING DATE"].max()
        maxPricingDateABSDeal = finsightAbbNIDeal["Pricing Date"].max()

        df = pd.DataFrame(columns=["res"])
        df.loc["Latest Pricing Date (Bond)"] = maxPricingDateABSBond

        df.loc["Latest Deal (Bond)"] = (
            finsightAbbNIBond[
                finsightAbbNIBond["PRICING DATE"] == maxPricingDateABSBond
            ]
            .head(1)["Deal Name"]
            .values[0]
        )

        df.loc["Latest Pricing Date (Deal)"] = maxPricingDateABSDeal

        df.loc["Latest Deal (Deal)"] = (
            finsightAbbNIDeal[
                finsightAbbNIDeal["Pricing Date"] == maxPricingDateABSDeal
            ]
            .head(1)["Deal Name"]
            .values[0]
        )

        df = df.reset_index()
        df = df.rename(columns={"index": "ChekItem", "res": "value"})

        return df
