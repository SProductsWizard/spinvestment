import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.db_driver import AtlasDriver


class SPCFdb_mgmt:
    def __init__(self):
        self.driver = AtlasDriver(readOnly=False)

    def load_assetRepline(self):
        return self.driver.load_data(colName="SPCF_assetRepline")
