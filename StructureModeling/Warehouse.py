import pandas as pd
import numpy as np
import numpy_financial as npf
import itertools
from copy import deepcopy


class WarehouseStructure:
    def __init__(self, rampPool, whTerms, exitDetails):
        self.rampPool = rampPool

        self.commitDetails = whTerms.get("commitDetails", {"period": 12})

        self.advRate = whTerms.get("advRate", {"Senior": 70, "Mezz": 85})

        self.coupon = whTerms.get("coupon", {"Senior": 0.05, "Mezz": 0.1})

        self.undrawnFee = whTerms.get("undrawnFee", {"Senior": 0.01, "Mezz": 0.01})

        self.facilitySize = whTerms.get("facilitySize", {"Senior": 1e9, "Mezz": 1e9})

        self.transactionFees = whTerms.get(
            "transactionFees",
            {
                "feeRatios": {
                    "trustee": 0.01,
                    "verificationAgent": 0.005,
                    "backupServicingStandby": 0.0025,
                    "breakupFeesPct": 0.01,
                },
                "feeDollars": {
                    "legalClosing": 100000,
                    "trustSetup": 10000,
                    "verificationAgentSetup": 10000,
                    "backupServicerSetup": 5000,
                    "breakupFees": 50000,
                },
            },
        )

        self.covenants = whTerms.get("covenants", {"CNL": [], "DQ": []})

        self.exitPeriods = exitDetails.get("exitPeriods", {"periods": []})
        self.exitPx = exitDetails.get("exitPx", {"px": []})
        self.exitUnderwritingFees = exitDetails.get(
            "exitUnderwritingFees", {"fees": []}
        )
        self.exitCreditBox = exitDetails.get(
            "exitCreditBox",
            {
                "WALA": [],
                "DQ": [],
            },
        )

        self._enrichWhTerms()
        self._buildCashflow()
        self.warehouseStats = self._buildStats()

    def _enrichWhTerms(self):
        self.feesDollar = deepcopy(self.transactionFees["feeDollars"])
        self.upfrontFeesDollar = deepcopy(self.transactionFees["feeDollars"])
        self.upfrontFeesDollar.pop("breakupFees")

        self.feesRatio = deepcopy(self.transactionFees["feeRatios"])
        self.periodicFeesRatio = deepcopy(self.transactionFees["feeRatios"])
        self.periodicFeesRatio.pop("breakupFeesPct")

        self.advRateConvert = {}
        pre_adv = 0
        for tranche, adv in self.advRate.items():
            advCut = adv - pre_adv
            self.advRateConvert[tranche] = advCut
            pre_adv = adv

        self.effectiveLender = [k for k, v in self.advRateConvert.items() if v > 0]

        return self

    def _extendCashflowFramework(self):
        self.warehouseCashflow = self.rampPool.rampCashflow.copy()

        self.warehouseCashflow = self.warehouseCashflow.set_index("rampPeriod")
        self.warehouseCashflow.columns = pd.MultiIndex.from_product(
            [["Asset"], self.warehouseCashflow.columns]
        )

        feesColumns = list(
            itertools.product(
                ["Fees"],
                list(self.transactionFees["feeRatios"].keys())
                + list(self.transactionFees["feeDollars"].keys()),
            )
        )

        self.periodicFeesRatioColumns = list(
            itertools.product(["Fees"], list(self.periodicFeesRatio.keys()))
        )

        self.warehouseCashflow = self.warehouseCashflow.reindex(
            self.warehouseCashflow.columns.tolist() + feesColumns,
            axis=1,
        )

        warehouseLenderColumns = [
            "bopFacilitySize",
            "bopBal",
            "bopUndrawnAmount",
            "undrawnFeeDue",
            "undrawnFeePaid",
            "undrawnFeeShortfall",
            "couponDue",
            "couponPaid",
            "couponShortfall",
            "newDrawn",
            "requiredPaidDown",
            "paidDownPrin",
            "eopUndrawnAmount",
            "eopBal",
            "eopFacilitySize",
        ]

        lenderColumns = list(
            itertools.product(self.effectiveLender, warehouseLenderColumns)
        )

        self.warehouseCashflow = self.warehouseCashflow.reindex(
            self.warehouseCashflow.columns.tolist() + lenderColumns,
            axis=1,
        )

        residualColumns = list(
            itertools.product(
                ["Residual"], ["cashInvestment", "repaymentCash", "investmentCF"]
            )
        )

        self.warehouseCashflow = self.warehouseCashflow.reindex(
            self.warehouseCashflow.columns.tolist() + residualColumns,
            axis=1,
        )

        self.bopColumns = [
            col
            for col in self.warehouseCashflow.columns
            if ("bop" in col[1]) & (col[0] != "Asset")
        ]

        self.eopColumns = [
            col
            for col in self.warehouseCashflow.columns
            if ("eop" in col[1]) & (col[0] != "Asset")
        ]

    def _buildCashflow(self):
        self._extendCashflowFramework()

        lenderColumnsGroup = lambda x: list(
            itertools.product(self.effectiveLender, [x])
        )

        # loop through rampPeriod to calculate periodic cashflow
        for i, row in self.warehouseCashflow.iterrows():
            if i == 0:
                # set upfront fees
                upfrontFeesColumns = list(
                    itertools.product(["Fees"], self.upfrontFeesDollar)
                )

                row[upfrontFeesColumns] = list(self.upfrontFeesDollar.values())

                # set facility initial status
                row[lenderColumnsGroup("bopBal")] = 0

                row[lenderColumnsGroup("newDrawn")] = (
                    row[("Asset", "eopBal")]
                    * np.array([*self.advRateConvert.values()])
                    / 100.0
                )

                row[lenderColumnsGroup("eopBal")] = np.array(
                    row[lenderColumnsGroup("bopBal")]
                ) + np.array(row[lenderColumnsGroup("newDrawn")])

                row[lenderColumnsGroup("eopFacilitySize")] = [
                    self.facilitySize[k] for k in self.effectiveLender
                ]

                row[lenderColumnsGroup("eopUndrawnAmount")] = np.array(
                    row[lenderColumnsGroup("eopFacilitySize")]
                ) - np.array(row[lenderColumnsGroup("eopBal")])

                # set residual tranche initial status
                row[("Residual", "cashInvestment")] = -(
                    row[("Asset", "purchaseCash")] + sum(row[upfrontFeesColumns])
                ) + sum(row[lenderColumnsGroup("newDrawn")])

                row[("Residual", "repaymentCash")] = 0

                row[("Residual", "investmentCF")] = (
                    row[("Residual", "cashInvestment")]
                    + row[("Residual", "repaymentCash")]
                )

                row = row.fillna(0)

            else:
                # set bop balance
                row[self.bopColumns] = np.array(
                    self.warehouseCashflow.loc[i - 1, self.eopColumns]
                )

                row[self.periodicFeesRatioColumns] = (
                    row[("Asset", "bopBal")]
                    * np.array(list(self.periodicFeesRatio.values()))
                    / 12.0
                )

                row[lenderColumnsGroup("undrawnFeeDue")] = (
                    np.array(row[lenderColumnsGroup("bopUndrawnAmount")])
                    * np.array([self.undrawnFee[k] for k in self.effectiveLender])
                    / 12.0
                )

                row[lenderColumnsGroup("couponDue")] = (
                    np.array(row[lenderColumnsGroup("bopBal")])
                    * np.array([self.coupon[k] for k in self.effectiveLender])
                    / 12.0
                )

                #########################
                print(row)
                print("stop here")

                row = row.fillna(0)

            self.warehouseCashflow.loc[i] = row

        return self

    def _buildStats(self):
        warehouseStats = {}
        return warehouseStats
