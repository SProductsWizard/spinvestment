import pandas as pd
import numpy as np
import numpy_financial as npf
from copy import deepcopy


class AssetRamper:
    def __init__(self, sizeList, pxList, assetList):
        self.sizeList = sizeList
        self.ramp = len(self.sizeList)

        if len(pxList) != self.ramp:
            self.pxList = pxList[: self.ramp] + [pxList[-1]] * (self.ramp - len(pxList))
        else:
            self.pxList = pxList

        if len(assetList) != self.ramp:
            self.assetList = assetList[: self.ramp] + [deepcopy(assetList[-1])] * (
                self.ramp - len(assetList)
            )
        else:
            self.assetList = assetList

        self._buildRampCashflow()

    def addAsset(self, size, px, asset):
        self.sizeList.append(size)
        self.pxList.append(px)
        self.assetList.append(asset)
        self.rampCashflow = self._buildRampCashflow()

    def _buildRampCashflow(self):
        cfList = []
        rampPeriod = 0
        for asset, px, size in zip(self.assetList, self.pxList, self.sizeList):
            rampFactor = size / asset.notional
            cf = asset.cashflow.copy()

            cf[asset.dollarColumns] = cf[asset.dollarColumns] * rampFactor

            cf["rampSize"] = cf["period"].apply(lambda x: size if x == 0 else 0)
            cf["purchaseCash"] = px * cf["rampSize"] / 100

            cf["repaymentCash"] = cf["totalCF"]
            cf["rampPeriod"] = cf["period"] + rampPeriod
            cf["investmentCash"] = -cf["purchaseCash"] + cf["repaymentCash"]

            cf = cf[
                [
                    "period",
                    "rampPeriod",
                    "bopBal",
                    "intCF",
                    "prinCF",
                    "lossPrin",
                    "dqBal",
                    "cumulativeLossPrin",
                    "eopBal",
                    "rampSize",
                    "purchaseCash",
                    "repaymentCash",
                    "investmentCash",
                ]
            ]

            rampPeriod += 1

            cfList.append(cf)

        self.rampCashflowList = cfList

        temp = pd.concat(self.rampCashflowList, axis=0, ignore_index=True)

        self.rampCashflow = (
            temp.groupby(["rampPeriod"])
            .agg(
                bopBal=("bopBal", "sum"),
                intCF=("intCF", "sum"),
                prinCF=("prinCF", "sum"),
                lossPrin=("lossPrin", "sum"),
                dqBal=("dqBal", "sum"),
                cumulativeLossPrin=("cumulativeLossPrin", "sum"),
                eopBal=("eopBal", "sum"),
                rampSize=("rampSize", "sum"),
                purchaseCash=("purchaseCash", "sum"),
                repaymentCash=("repaymentCash", "sum"),
                investmentCash=("investmentCash", "sum"),
            )
            .reset_index()
        )

        return self
