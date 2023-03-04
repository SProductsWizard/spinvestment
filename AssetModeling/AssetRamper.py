import pandas as pd
import numpy as np
import numpy_financial as npf
from copy import deepcopy


class AssetRamper:
    def __init__(self, sizeList, pxList, assetList):
        self.sizeList = sizeList
        self.rampPeriod = len(self.sizeList)

        if len(pxList) != self.rampPeriod:
            self.pxList = pxList[: self.rampPeriod] + [pxList[-1]] * (
                self.rampPeriod - len(pxList)
            )
        else:
            self.pxList = pxList

        if len(assetList) != self.rampPeriod:
            self.assetList = assetList[: self.rampPeriod] + [
                deepcopy(assetList[-1])
            ] * (self.rampPeriod - len(assetList))
        else:
            self.assetList = assetList

        self._buildRampCashflow()
        self.rampStats = self._buildStats()

    # def addAsset(self, size, px, asset):
    #     self.sizeList.append(size)
    #     self.pxList.append(px)
    # self.assetList.append(asset)
    # self._buildRampCashflow()

    def _buildRampCashflow(self):
        cfList = []
        rampPeriod = 0
        for asset, px, size in zip(self.assetList, self.pxList, self.sizeList):
            rampFactor = size / asset.notional
            cf = asset.cashflow.copy()

            cf[asset.dollarColumns] = cf[asset.dollarColumns] * rampFactor

            cf["rampSize"] = cf["period"].apply(lambda x: size if x == 0 else 0)
            cf["purchasePx"] = cf["period"].apply(lambda x: px if x == 0 else np.nan)
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
                    "netIntCF",
                    "prinCF",
                    "lossPrin",
                    "dqBal",
                    "eopBal",
                    "rampSize",
                    "purchasePx",
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
                netIntCF=("netIntCF", "sum"),
                prinCF=("prinCF", "sum"),
                lossPrin=("lossPrin", "sum"),
                dqBal=("dqBal", "sum"),
                eopBal=("eopBal", "sum"),
                rampSize=("rampSize", "sum"),
                purchasePx=("purchasePx", "sum"),
                purchaseCash=("purchaseCash", "sum"),
                repaymentCash=("repaymentCash", "sum"),
                investmentCash=("investmentCash", "sum"),
            )
            .reset_index()
        )
        self.rampCashflow["cumulativeLossPrin"] = self.rampCashflow["lossPrin"].cumsum()
        self.rampCashflow["cumulativeInvestmentCash"] = self.rampCashflow[
            "investmentCash"
        ].cumsum()

        return self

    def _buildStats(self):
        rampStats = {"metrics": {}, "ts_metrics": {}}
        rampStats["metrics"]["Commit Period"] = self.rampPeriod

        rampStats["metrics"]["Unlevered Yield"] = (
            npf.irr(self.rampCashflow["investmentCash"].values) * 12
        )
        rampStats["metrics"]["Breakeven Period"] = self.rampCashflow[
            self.rampCashflow["cumulativeInvestmentCash"] > 0
        ]["rampPeriod"].min()

        rampStats["metrics"]["Total Purchase Balance"] = self.rampCashflow[
            "rampSize"
        ].sum()
        rampStats["metrics"]["Total Purchase Basis"] = self.rampCashflow[
            "purchaseCash"
        ].sum()
        rampStats["metrics"]["Avg Purchase Px"] = 100 * (
            rampStats["metrics"]["Total Purchase Basis"]
            / rampStats["metrics"]["Total Purchase Balance"]
        )

        rampStats["metrics"]["Total Int Repayment"] = self.rampCashflow[
            "netIntCF"
        ].sum()
        rampStats["metrics"]["Total Prin Repayment"] = self.rampCashflow["prinCF"].sum()
        rampStats["metrics"]["Total Repayment"] = self.rampCashflow[
            "repaymentCash"
        ].sum()

        rampStats["metrics"]["Total PnL"] = self.rampCashflow["investmentCash"].sum()

        rampStats["metrics"]["Total Loss"] = self.rampCashflow["lossPrin"].sum()
        rampStats["metrics"]["Avg CNL"] = (
            rampStats["metrics"]["Total Loss"]
            / rampStats["metrics"]["Total Purchase Balance"]
        )

        rampStats["ts_metrics"]["investmentCFCurve"] = self.rampCashflow[
            ["rampPeriod", "cumulativeInvestmentCash"]
        ]

        rampStats["ts_metrics"]["portfolioBalanceCurve"] = self.rampCashflow[
            ["rampPeriod", "bopBal"]
        ]

        rampStats["ts_metrics"]["repaymentCurve"] = self.rampCashflow[
            ["rampPeriod", "netIntCF", "prinCF"]
        ]

        rampStats["ts_metrics"]["dollarLossCurve"] = self.rampCashflow[
            ["rampPeriod", "cumulativeLossPrin"]
        ]
        return rampStats

    def getStaticMetrics(self):

        df = pd.DataFrame([self.rampStats["metrics"]]).T

        df = df.reset_index()
        df.columns = ["metrics", "value"]
        return df
