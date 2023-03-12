import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from DatabaseManagement.model.abs_scrap import ABSScrap
from DatabaseManagement.db_driver import AtlasDriver


def updateABSData():

    bondDf = ABSScrap().runScrapBond(urlAssetClass="ABS", cutDate="2023-03-06")
    dealDf = ABSScrap().runScrapDeal(cutDate="2023-03-06")

    driver = AtlasDriver()
    driver.upload_data_NIBond(bondDf)
    driver.upload_data_NIDeal(dealDf)


def deleteABSData():
    driver = AtlasDriver()
    driver.delete_data_NIBond(cutDate="2023-03-06")
    driver.delete_data_NIDeal(cutDate="2023-03-06")


if __name__ == "__main__":
    updateABSData()
