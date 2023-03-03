import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.db_driver import AtlasDriver


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
