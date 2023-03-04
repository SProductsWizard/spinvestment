import pandas as pd
import numpy as np
import numpy_financial as npf


class Asset:
    def __init__(self):
        pass


class AmortizationAsset(Asset):
    def __init__(self, notional, term, intRate, **kwargs):
        self.notional = notional
        self.term = term
        self.intRate = intRate
        self.cdrVector = kwargs.get("cdrVector")
        self.cprVector = kwargs.get("cprVector")
        self.sevVector = kwargs.get("sevVector")
        self.dqVector = kwargs.get("dqVector")
        self.servicingFeesRatio = kwargs.get("servicingFeesRatio")
        if self.servicingFeesRatio is None:
            self.servicingFeesRatio = 0.008

        self.cashflow = self._buildCashflow()
        self.assetStats = self._buildStats()

        self.modelingWarning = {}

    def _buildCashflow(self):
        amortSchedPeriodic = np.concatenate(
            [
                np.array([0]),
                npf.ppmt(
                    self.intRate / 12,
                    np.arange(self.term) + 1,
                    self.term,
                    -self.notional,
                ),
            ]
        )
        periods = np.array(range(0, self.term + 1))
        cdrVector = np.concatenate([np.array([0]), np.array(self.cdrVector)])
        mdrVector = 1 - (1 - cdrVector) ** (1 / 12)
        cprVector = np.concatenate([np.array([0]), np.array(self.cprVector)])
        smmVector = 1 - (1 - cprVector) ** (1 / 12)
        sevVector = np.concatenate([np.array([0]), np.array(self.sevVector)])
        dqVector = np.concatenate([np.array([0]), np.array(self.dqVector)])

        cashflow = pd.DataFrame(
            list(
                zip(
                    periods,
                    amortSchedPeriodic,
                    cdrVector,
                    mdrVector,
                    cprVector,
                    smmVector,
                    sevVector,
                    dqVector,
                )
            ),
            columns=[
                "period",
                "amortSchedPeriodic",
                "cdrVector",
                "mdrVector",
                "cprVector",
                "smmVector",
                "sevVector",
                "dqVector",
            ],
        )

        cashflow["amortBalPeriodic"] = (
            self.notional - cashflow["amortSchedPeriodic"].cumsum()
        )
        cashflow["balFactor"] = (
            cashflow["amortBalPeriodic"]
            .div(cashflow["amortBalPeriodic"].shift())
            .fillna(1)
        )

        cashflow[
            [
                "bopBal",
                "perfBal",
                "dqBal",
                "prepayPrin",
                "intCF",
                "servicingFees",
                "netIntCF",
                "defaultPrin",
                "lossPrin",
                "recoveryPrin",
                "schedPrin",
                "prinCF",
                "eopBal",
            ]
        ] = np.nan
        cashflow[["servicingFeesRatio"]] = self.servicingFeesRatio

        for i, row in cashflow.iterrows():

            if row["period"] == 0:
                cashflow.loc[
                    i,
                    [
                        "bopBal",
                        "perfBal",
                        "dqBal",
                        "prepayPrin",
                        "intCF",
                        "servicingFees",
                        "netIntCF",
                        "defaultPrin",
                        "lossPrin",
                        "recoveryPrin",
                        "schedPrin",
                        "prinCF",
                    ],
                ] = 0
                cashflow.at[i, "eopBal"] = self.notional
            else:
                cashflow.at[i, "bopBal"] = cashflow.loc[i - 1, "eopBal"]
                cashflow.at[i, "defaultPrin"] = (
                    cashflow.at[i, "bopBal"] * cashflow.at[i, "mdrVector"]
                )
                nonDefaultPrin = (
                    cashflow.at[i, "bopBal"] - cashflow.at[i, "defaultPrin"]
                )

                cashflow.at[i, "lossPrin"] = (
                    cashflow.at[i, "defaultPrin"] * cashflow.at[i, "sevVector"]
                )
                cashflow.at[i, "recoveryPrin"] = (
                    cashflow.at[i, "defaultPrin"] - cashflow.at[i, "lossPrin"]
                )

                cashflow.at[i, "perfBal"] = nonDefaultPrin * (
                    1 - cashflow.at[i, "dqVector"]
                )
                cashflow.at[i, "dqBal"] = nonDefaultPrin - cashflow.at[i, "perfBal"]

                cashflow.at[i, "intCF"] = cashflow.at[i, "perfBal"] * self.intRate / 12

                cashflow.at[i, "prepayPrin"] = (
                    cashflow.at[i, "perfBal"] * cashflow.at[i, "smmVector"]
                )
                cashflow.at[i, "schedPrin"] = (
                    nonDefaultPrin - cashflow.at[i, "prepayPrin"]
                ) * (1 - cashflow.at[i, "balFactor"])

                cashflow.at[i, "prinCF"] = (
                    cashflow.at[i, "schedPrin"]
                    + cashflow.at[i, "recoveryPrin"]
                    + cashflow.at[i, "prepayPrin"]
                )
                cashflow.at[i, "eopBal"] = (
                    cashflow.at[i, "bopBal"]
                    - cashflow.at[i, "schedPrin"]
                    - cashflow.at[i, "defaultPrin"]
                    - cashflow.at[i, "prepayPrin"]
                )

                cashflow.at[i, "servicingFees"] = (
                    np.average([cashflow.at[i, "bopBal"], cashflow.at[i, "eopBal"]])
                    * cashflow.at[i, "servicingFeesRatio"]
                    / 12.0
                )

                cashflow.at[i, "netIntCF"] = (
                    cashflow.at[i, "intCF"] - cashflow.at[i, "servicingFees"]
                )

        # cashflow["intCF"] = cashflow["perfBal"] * self.intRate / 12
        cashflow["grossTotalCF"] = cashflow["intCF"] + cashflow["prinCF"]
        cashflow["totalCF"] = cashflow["netIntCF"] + cashflow["prinCF"]

        cashflow["cumulativeLossPrin"] = cashflow["lossPrin"].cumsum()
        cashflow["cnl"] = cashflow["cumulativeLossPrin"] / self.notional
        cashflow["factor"] = cashflow["eopBal"] / self.notional
        cashflow["ltl"] = cashflow["cnl"] / (1 - cashflow["factor"])

        self.dollarColumns = [
            "bopBal",
            "eopBal",
            "perfBal",
            "dqBal",
            "prepayPrin",
            "intCF",
            "servicingFees",
            "netIntCF",
            "defaultPrin",
            "lossPrin",
            "recoveryPrin",
            "schedPrin",
            "prinCF",
            "grossTotalCF",
            "totalCF",
            "cumulativeLossPrin",
        ]

        return cashflow

    def _buildStats(self):
        assetStats = {"metrics": {}, "ts_metrics": {}}
        assetStats["metrics"]["notional"] = self.notional
        assetStats["metrics"]["wal"] = (
            (self.cashflow["prinCF"] * self.cashflow["period"]).sum()
            / self.cashflow["prinCF"].sum()
            / 12.0
        )

        assetStats["metrics"]["intRate"] = self.intRate
        assetStats["metrics"]["term"] = self.term

        assetStats["metrics"]["intPmt"] = self.cashflow["intCF"].sum()
        assetStats["metrics"]["prinPmt"] = self.cashflow["prinCF"].sum()
        assetStats["metrics"]["totalPmt"] = self.cashflow["totalCF"].sum()

        assetStats["metrics"]["totalDefault"] = self.cashflow["defaultPrin"].sum()
        assetStats["metrics"]["totalLoss"] = self.cashflow["lossPrin"].sum()
        assetStats["metrics"]["cnl"] = self.cashflow["lossPrin"].sum() / self.notional

        assetStats["ts_metrics"]["cdrCurve"] = self.cashflow[["period", "cdrVector"]]
        assetStats["ts_metrics"]["cprCurve"] = self.cashflow[["period", "cprVector"]]
        assetStats["ts_metrics"]["sevCurve"] = self.cashflow[["period", "sevVector"]]
        assetStats["ts_metrics"]["dqCurve"] = self.cashflow[["period", "dqVector"]]
        assetStats["ts_metrics"]["cnlCurve"] = self.cashflow[["period", "cnl", "ltl"]]
        assetStats["ts_metrics"]["ltlCurve"] = self.cashflow[["period", "ltl"]]
        assetStats["ts_metrics"]["factorCurve"] = self.cashflow[["period", "factor"]]

        return assetStats

    def getStaticMetrics(self):

        df = pd.DataFrame([self.assetStats["metrics"]]).T

        df = df.reset_index()
        df.columns = ["matrics", "value"]
        return df

    def calculateYield(self, px):
        calcdf = self.cashflow[["period", "totalCF"]]
        calcdf.loc[calcdf["period"] == 0, "totalCF"] = -1 * self.notional * px / 100.0
        calcirr = npf.irr(calcdf["totalCF"].values) * 12

        return calcirr

    def calculateYieldTable(self, pxList):
        yieldList = [self.calculateYield(px) for px in pxList]
        return pd.DataFrame({"px": pxList, "yield": yieldList})
