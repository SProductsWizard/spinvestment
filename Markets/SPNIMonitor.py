import numpy as np
import pandas as pd
import datetime

from DatabaseManagement.db_driver import AtlasDriver
from Markets.config import RatingsConvert
from Utils.SPCFUtils import SPCFUtils


class ABSNIMonitor:
    def __init__(self):
        self.atlasDriver = AtlasDriver(readOnly=True)
        self.ABSNIBondDfRaw = self.atlasDriver.load_data("FinsightNIBond")
        self.ABSNIDealDfRaw = self.atlasDriver.load_data("FinsightNIDeal")

        self.RMBSNIBondDfRaw = self.atlasDriver.load_data("FinsightNIBond_RMBS")
        self.RMBSNIDealDfRaw = self.atlasDriver.load_data("FinsightNIDeal_RMBS")
        self.cdxData = self.atlasDriver.load_data("CDX_Index")
        self.cdxData["Date"] = self.cdxData["Date"].dt.normalize()

        self.ABSNIBondDf, self.ABSNIDealDf = self._cleanData(self.ABSNIBondDfRaw, self.ABSNIDealDfRaw)
        self.RMBSNIBondDf, self.RMBSNIDealDf = self._cleanData(self.RMBSNIBondDfRaw, self.RMBSNIDealDfRaw)
        self.ABSNIBondDf = self._enrichData(self.ABSNIBondDf, self.ABSNIDealDf)
        self.RMBSNIBondDf = self._enrichData(self.RMBSNIBondDf, self.RMBSNIDealDf)

    def getCdxIG(self):
        return (
            self.cdxData[["Date", "CDX_IG"]]
            .sort_values(by="Date", ascending=False)
            .copy()
        )

    def getCdxHY(self):
        return (
            self.cdxData[["Date", "CDX_HY"]]
            .sort_values(by="Date", ascending=False)
            .copy()
        )

    @staticmethod
    def _cleanData(bond_df_raw, deal_df_raw):
        # CDX Data Table
        # self.cdxData["Date"] = self.cdxData["Date"].dt.normalize()

        # Deal Table
        deal_df = deal_df_raw[
            ["Deal Name", "Sector", "Subsector", "Issuer Name", "Pricing Date"]
        ]
        deal_df["Deal Name"] = deal_df["Deal Name"].str.strip()
        deal_df["PRICING DATE"] = deal_df["Pricing Date"]

        # Bond Table
        df = bond_df_raw.copy()
        df["Deal Name"] = df["Deal Name"].str.strip()

        # merge deal and bond table --> bond table
        df = df.merge(
            deal_df[
                ["Deal Name", "PRICING DATE", "Sector", "Subsector", "Issuer Name"]
            ],
            on=["Deal Name", "PRICING DATE"],
            how="left",
        ).dropna(subset=["Sector", "Subsector", "Issuer Name"])

        # Issuer Name Short
        df["IssuerShort"] = df["Issuer Name"].apply(
            lambda x: x.split(" ")[0]
        )

        # Shelf
        df["Shelf"] = df["Deal Name"].apply(
            lambda x: x.split(" ")[0]
        )

        # sze (m) --> sze
        df["SZE 1"] = df["SZE (M)"].apply(
            lambda x: 0 if np.isnan(x) else x * 1e6
        )

        if "SZE(M)" in df.columns:
            df["SZE 2"] = df["SZE(M)"].apply(
                lambda x: float(x.replace(",", "")) * 1e6 if isinstance(x, str) else 0
            )

            df["SZE"] = df["SZE 1"] + df["SZE 2"]
            df = df.drop(
                columns=["SZE 1", "SZE 2", "SZE (M)", "SZE(M)"], axis=1
            )
        else:
            df["SZE"] = df["SZE 1"]
            df = df.drop(
                columns=["SZE 1", "SZE (M)"], axis=1
            )

        df["SZE(M)"] = df["SZE"] / 1e6

        # Pricing Year
        df["PRICING YEAR"] = df["PRICING DATE"].apply(
            lambda x: x.year
        )

        # Pricing Day of Year
        df["PRICING DAY OF YEAR"] = df[
            "PRICING DATE"
        ].apply(lambda x: x.dayofyear)

        # Spread
        df["Spread"] = df["SPRD"].apply(
            lambda x: x
            if isinstance(x, float)
            else SPCFUtils.convertSPRD(x.replace(",", ""))
        )

        # WAL
        df["Wal"] = df["WAL"].apply(
            lambda x: x
            if isinstance(x, float)
            else SPCFUtils.convertWAL(x.replace(",", ""))
        )

        return df, deal_df

    def _enrichData(self, df, deal_df):

        # Ratings
        ratingAgencyShortLong = {
            "MO": "MoodysRatings",
            "SP": "SPRatings",
            "FI": "FitchRatings",
            "KR": "KBRARatings",
            "DR": "DBRSRatings",
        }

        for ratingAgency in ["MO", "SP", "FI", "KR", "DR"]:
            ratingAgencyLong = ratingAgencyShortLong[ratingAgency]
            ratingConvertDict = RatingsConvert[ratingAgencyLong]
            df[f"{ratingAgency}Convert"] = df[
                ratingAgency
            ].apply(
                lambda x: ratingConvertDict[x]
                if x in ratingConvertDict.keys()
                else "NR"
            )

        ratingScale = RatingsConvert["RatingsRank"]
        scaleRating = {v: k for k, v in ratingScale.items()}

        df["HighestRatings"] = df.apply(
            lambda x: scaleRating[
                SPCFUtils.findRatingsMinMax(
                    [
                        ratingScale[x["MOConvert"]],
                        ratingScale[x["SPConvert"]],
                        ratingScale[x["FIConvert"]],
                        ratingScale[x["KRConvert"]],
                        ratingScale[x["DRConvert"]],
                    ]
                )
            ],
            axis=1,
        )

        df["LowestRatings"] = df.apply(
            lambda x: scaleRating[
                SPCFUtils.findRatingsMinMax(
                    [
                        ratingScale[x["MOConvert"]],
                        ratingScale[x["SPConvert"]],
                        ratingScale[x["FIConvert"]],
                        ratingScale[x["KRConvert"]],
                        ratingScale[x["DRConvert"]],
                    ],
                    findMin=False,
                )
            ],
            axis=1,
        )

        self._latestYears = [2019, 2020, 2021, 2022]
        self._subigRatings = ["BB", "B", "CCC", "CC", "C", "NR"]
        self._belowAAIgRatings = ["A", "BBB"]
        '''
        self._subprimeAutoTop10Shelf = list(
            self.runPrecannedStats(order="SubprimeAutoIssuer").index[0:10]
        )
        self._consumerLoanTop10Shelf = list(
            self.runPrecannedStats(order="consumerLoanIssuer").index[0:10]
        )

        #resi
        self._privateRMBSTop10Shelf = list(
            self.runPrecannedStats(order="PerformingLoanIssuer").index[0:10]
        )
        '''
        self.latestPricingDate = deal_df["PRICING DATE"].max()
        self.latestBondPricingDate = df["PRICING DATE"].max()

        self.relValSector = [
            "subprimeAuto",
            "consumerLoan",
            "rentalCar",
            "wholeBiz",
            # "solar",
            "smallBiz",
        ]
        return df

    def databaseStatus(self):
        df = pd.DataFrame(columns=["res"])
        df.loc["Latest Pricing Date (Deal)"] = self.latestPricingDate
        df.loc["Latest Deal Name (Deal)"] = (
            self.ABSNIDealDf[self.ABSNIDealDf["PRICING DATE"] == self.latestPricingDate]
            .head(1)["Deal Name"]
            .values[0]
        )
        df.loc["Latest Pricing Date (Bond)"] = self.latestBondPricingDate
        df.loc["Latest Deal Name (Bond)"] = (
            self.ABSNIBondDfRaw[
                self.ABSNIBondDfRaw["PRICING DATE"] == self.latestBondPricingDate
            ]
            .head(1)["Deal Name"]
            .values[0]
        )

        df = df.reset_index()
        return df

    def screenBonds(self, numBackDays, ratingsList, endDate=""):
        if endDate == "":
            endDate = self.latestPricingDate
        else:
            endDate = pd.to_datetime(endDate)

        pricingDateList = [
            endDate - datetime.timedelta(days=x) for x in range(numBackDays)
        ]

        return self.ABSNIBondDf[
            (self.ABSNIBondDf["PRICING DATE"].isin(pricingDateList))
            & (self.ABSNIBondDf["LowestRatings"].isin(ratingsList))
            & (self.ABSNIBondDf["Subsector"].isin(self.relValSector))
        ]
   #resi 
    def screenRMBSBonds(self, numBackDays, ratingsList, endDate="",relValSector=['Performing','CRT','PrimeJumbo']):
        if endDate == "":
            endDate = self.latestPricingDate
        else:
            endDate = pd.to_datetime(endDate)

        pricingDateList = [
            endDate - datetime.timedelta(days=x) for x in range(numBackDays)
        ]

        return self.RMBSNIBondDf[
            (self.RMBSNIBondDf["PRICING DATE"].isin(pricingDateList))
            & (self.RMBSNIBondDf["LowestRatings"].isin(ratingsList))
            & (self.RMBSNIBondDf["Subsector"].isin(relValSector))
        ]
    

    def runRMBSRelVal(self, numBackDays, endDate=""):
        relValBonds = self.screenRMBSBonds(
            numBackDays=numBackDays, ratingsList=["A", "BBB", "BB","B"], endDate=endDate
        )[["PRICING DATE", "Subsector", "LowestRatings", "Wal", "Spread", "SZE"]]

        weights = lambda x: SPCFUtils.weightAvg(x, relValBonds, "SZE")

        return (
            relValBonds.groupby(["Subsector", "LowestRatings"])
            .agg(Spread=("Spread", weights), WAL=("Wal", weights))
            .reset_index()
        )

    

    def runRelVal(self, numBackDays, endDate=""):
        relValBonds = self.screenBonds(
            numBackDays=numBackDays, ratingsList=["A", "BBB", "BB"], endDate=endDate
        )[["PRICING DATE", "Subsector", "LowestRatings", "Wal", "Spread", "SZE"]]

        weights = lambda x: SPCFUtils.weightAvg(x, relValBonds, "SZE")

        return (
            relValBonds.groupby(["Subsector", "LowestRatings"])
            .agg(Spread=("Spread", weights), WAL=("Wal", weights))
            .reset_index()
        )

    def runStatsEngine(
        self,
        fieldCalc=("SZE", "sum"),
        groupBy=[],
        filter={},
    ):
        if filter == {}:
            filteredABSNIBond = self.ABSNIBondDf
        else:
            filteredABSNIBond = self.ABSNIBondDf.copy()
            for k, v in filter.items():
                filteredABSNIBond = filteredABSNIBond[filteredABSNIBond[k].isin(v)]

        return filteredABSNIBond.groupby(groupBy).agg(res=fieldCalc)
    
    #resi
    def runRMBSStatsEngine(
        self,
        fieldCalc=("SZE", "sum"),
        groupBy=[],
        filter={},
    ):
        if filter == {}:
            filteredRMBSNIBond = self.RMBSNIBondDf
        else:
            filteredRMBSNIBond = self.RMBSNIBondDf.copy()
            for k, v in filter.items():
                filteredRMBSNIBond = filteredRMBSNIBond[filteredRMBSNIBond[k].isin(v)]

        return filteredRMBSNIBond.groupby(groupBy).agg(res=fieldCalc)

    def runABSSectorSpread(self, ratings, subsector):
        return self.runStatsEngine(
            fieldCalc=("Spread", "mean"),
            groupBy=["PRICING DATE", "Deal Name"],
            filter={
                "Subsector": subsector,
                "PRICING YEAR": self._latestYears + [2023],
                "HighestRatings": ratings,
                "Shelf": list(self.runPrecannedStats(order=fr"{subsector[0]}Issuer").index[0:10]),
            },
        )    
    
    def runRMBSSectorSpread(self, ratings, subsector):
        return self.runRMBSStatsEngine(
            fieldCalc=("Spread", "mean"),
            groupBy=["PRICING DATE", "Deal Name"],
            filter={
                "Subsector": subsector,
                "PRICING YEAR": self._latestYears + [2023],
                "HighestRatings": ratings,
                "Shelf": list(self.runPrecannedStats(order=fr"{subsector[0]}LoanIssuer").index[0:10]),
            },
        )

    def getDisplayDf(self, head=None):
        df = self.ABSNIBondDf[
            [
                "Sector",
                "Subsector",
                "PRICING DATE",
                "Deal Name",
                "Class",
                "SZE(M)",
                "WAL",
                "MO",
                "SP",
                "FI",
                "DR",
                "KR",
                "MS",
                "LowestRatings",
                "FX/FL",
                "BNCH",
                "SPRD",
                "CPN",
                "YLD",
            ]
        ].copy()
        df = df.sort_values(
            by=["PRICING DATE", "Deal Name", "Class"], ascending=[False, True, True]
        )
        if head is None:
            return df
        else:
            df = df.head(head)

        return df

    def runsubsectorVolume(
        self, subsector, pricingyear=[2018, 2019, 2020, 2021, 2022, 2023]
    ):
        return self.runStatsEngine(
            groupBy=["PRICING YEAR"],
            filter={
                "Subsector": [subsector],
                "PRICING YEAR": pricingyear,
            },
        )
    #resi
    def runsubsectorVolumeRMBS(self, subsector, pricingyear=[ 2019, 2020, 2021, 2022, 2023]):
        #return self.RMBSNIBondDf[['PRICING YEAR', 'SZE(M)','Subsector']].groupby(by=['PRICING YEAR','Subsector']).sum()
        return self.runRMBSStatsEngine(
            groupBy=["PRICING YEAR"],
            filter={
                "Subsector": [subsector],
                "PRICING YEAR": pricingyear,
            },
        )

    def runRmbsBB_BBB_Spread(self, subsector):
        bbbSpread = (
            self.runPrecannedStats(order=fr"{subsector.lower()}BBBSpread")
            .reset_index()
            .rename(columns={"res": "bbbSpread"})
        )
        bbSpread = (
            self.runPrecannedStats(order=fr"{subsector.lower()}BBSpread")
            .reset_index()
            .rename(columns={"res": "bbSpread"})
        )
        bb_bbb_Spread = bbSpread.merge(
            bbbSpread,
            on=["PRICING DATE", "Deal Name"],
            how="left",
        )
        bb_bbb_Spread["bb_bbb_spread"] = (
            bb_bbb_Spread["bbSpread"] - bb_bbb_Spread["bbbSpread"]
        )

        bb_bbb_Spread = (
            bb_bbb_Spread.drop(["bbSpread", "bbbSpread"], axis=1)
            .rename(columns={"bb_bbb_spread": "res"})
            .set_index(["PRICING DATE", "Deal Name"])
        )
        bb_bbb_Spread = bb_bbb_Spread[~np.isnan(bb_bbb_Spread["res"])]

        return bb_bbb_Spread

    def runPrecannedStats(self, order):
        if order == "":
            temp = self.runStatsEngine(groupBy=["PRICING YEAR"], filter={})
            temp["res"] = np.nan
            return temp

        elif order == "ABSAnnualNI":
            return self.runStatsEngine(groupBy=["PRICING YEAR"], filter={})

        elif order == "ABSNI202320222021Vintage":
            temp = self.runStatsEngine(
                groupBy=["PRICING YEAR", "PRICING DAY OF YEAR"],
                filter={"PRICING YEAR": [2020, 2021, 2022, 2023]},
                fieldCalc=("SZE", "sum"),
            )
            temp = temp.reset_index()
            temp = temp.pivot(
                index="PRICING DAY OF YEAR", columns="PRICING YEAR", values="res"
            )

            latestDayOfYear_2023 = max(temp[~temp[2023].isnull()].index)
            temp = temp.fillna(value=0)
            temp = temp.cumsum()
            temp.loc[temp.index > latestDayOfYear_2023, 2023] = np.nan

            return temp

        elif order == "ABSNI20222021":
            tempdf = (
                self.runStatsEngine(
                    groupBy=["Subsector", "PRICING YEAR"],
                    filter={"PRICING YEAR": [2021, 2022]},
                )
                .unstack()
                .fillna(0)
                .sort_values(("res", 2022), ascending=True)
                .stack()
                .reset_index()
            )

            tempdf["PRICING YEAR"] = tempdf["PRICING YEAR"].apply(
                lambda x: "Yr_" + str(x)
            )

            return tempdf

        elif order == "ABSNIRatings":
            return self.runStatsEngine(
                groupBy=["HighestRatings"], filter={"PRICING YEAR": self._latestYears}
            )

        elif order == "ABSNISubsectorRatings":
            return self.runStatsEngine(
                groupBy=["Subsector", "HighestRatings"],
                filter={"PRICING YEAR": self._latestYears},
            )

        elif order == "ABSNISubsectorSubIG":
            temp = self.runStatsEngine(
                groupBy=["Subsector"],
                filter={
                    "PRICING YEAR": self._latestYears,
                    "HighestRatings": self._subigRatings,
                },
            )
            temp["res"] = temp["res"] / len(self._latestYears)
            temp = temp.sort_values(by="res", ascending=True)
            return temp

        elif order == "ABSNISubsectorBelowAAIG":
            temp = self.runStatsEngine(
                groupBy=["Subsector"],
                filter={
                    "PRICING YEAR": self._latestYears,
                    "HighestRatings": self._belowAAIgRatings,
                },
            )
            temp["res"] = temp["res"] / len(self._latestYears)
            temp = temp.sort_values(by="res", ascending=True)
            return temp

        elif order == "subprimeAutoIssuer":
            return self.runStatsEngine(
                groupBy=["Shelf"],
                filter={
                    "Subsector": ["subprimeAuto"],
                    "PRICING YEAR": self._latestYears,
                },
            ).sort_values(by="res", ascending=False)

        elif order == "consumerLoanIssuer":
            return self.runStatsEngine(
                groupBy=["Shelf"],
                filter={
                    "Subsector": ["consumerLoan"],
                    "PRICING YEAR": self._latestYears,
                },
            ).sort_values(by="res", ascending=False)

        elif order == "ConsumerLoanBBBSpread":
            return self.runABSSectorSpread(ratings=["BBB"], subsector=["consumerLoan"])

        elif order == "ConsumerLoanBBSpread":
            return self.runABSSectorSpread(ratings=["BB"], subsector=["consumerLoan"])

        elif order == "ConsumerLoanBB_BBBSpread":
            bbbSpread = (
                self.runPrecannedStats(order="ConsumerLoanBBBSpread")
                .reset_index()
                .rename(columns={"res": "bbbSpread"})
            )
            bbSpread = (
                self.runPrecannedStats(order="ConsumerLoanBBSpread")
                .reset_index()
                .rename(columns={"res": "bbSpread"})
            )
            bb_bbb_Spread = bbSpread.merge(
                bbbSpread,
                on=["PRICING DATE", "Deal Name"],
                how="left",
            )
            bb_bbb_Spread["bb_bbb_spread"] = (
                bb_bbb_Spread["bbSpread"] - bb_bbb_Spread["bbbSpread"]
            )

            bb_bbb_Spread = (
                bb_bbb_Spread.drop(["bbSpread", "bbbSpread"], axis=1)
                .rename(columns={"bb_bbb_spread": "res"})
                .set_index(["PRICING DATE", "Deal Name"])
            )
            bb_bbb_Spread = bb_bbb_Spread[~np.isnan(bb_bbb_Spread["res"])]

            return bb_bbb_Spread

        elif order == "SubprimeAutoBBBSpread":
            return self.runABSSectorSpread(ratings=["BBB"], subsector=["subprimeAuto"])

        elif order == "SubprimeAutoBBSpread":
            return self.runABSSectorSpread(ratings=["BB"], subsector=["subprimeAuto"])

        elif order == "SubprimeAutoBB_BBBSpread":
            bbbSpread = (
                self.runPrecannedStats(order="SubprimeAutoBBBSpread")
                .reset_index()
                .rename(columns={"res": "bbbSpread"})
            )
            bbSpread = (
                self.runPrecannedStats(order="SubprimeAutoBBSpread")
                .reset_index()
                .rename(columns={"res": "bbSpread"})
            )
            bb_bbb_Spread = bbSpread.merge(
                bbbSpread,
                on=["PRICING DATE", "Deal Name"],
                how="left",
            )
            bb_bbb_Spread["bb_bbb_spread"] = (
                bb_bbb_Spread["bbSpread"] - bb_bbb_Spread["bbbSpread"]
            )

            bb_bbb_Spread = (
                bb_bbb_Spread.drop(["bbSpread", "bbbSpread"], axis=1)
                .rename(columns={"bb_bbb_spread": "res"})
                .set_index(["PRICING DATE", "Deal Name"])
            )
            bb_bbb_Spread = bb_bbb_Spread[~np.isnan(bb_bbb_Spread["res"])]

            return bb_bbb_Spread
        
        elif order == "RMBSNI2023202220212020Vintage":
            temp = self.runRMBSStatsEngine(
                groupBy=["PRICING YEAR", "PRICING DAY OF YEAR"],
                filter={"PRICING YEAR": [2020, 2021, 2022, 2023]},
                fieldCalc=("SZE", "sum"),
            )
            temp = temp.reset_index()
            temp = temp.pivot(
                index="PRICING DAY OF YEAR", columns="PRICING YEAR", values="res"
            )

            latestDayOfYear_2023 = max(temp[~temp[2023].isnull()].index)
            temp = temp.fillna(value=0)
            temp = temp.cumsum()
            temp.loc[temp.index > latestDayOfYear_2023, 2023] = np.nan

            return temp

        elif order == "RMBSNISubsectorSubIG":
            temp = self.runRMBSStatsEngine(
                groupBy=["Subsector"],
                filter={
                    "PRICING YEAR": self._latestYears,
                    "HighestRatings": self._subigRatings,
                },
            )
            temp["res"] = temp["res"] / len(self._latestYears)
            temp = temp.sort_values(by="res", ascending=True)
            return temp
        
        elif order == "RMBSNISubsectorBelowAAIG":
            temp = self.runRMBSStatsEngine(
                groupBy=["Subsector"],
                filter={
                    "PRICING YEAR": self._latestYears,
                    "HighestRatings": self._belowAAIgRatings,
                },
            )
            temp["res"] = temp["res"] / len(self._latestYears)
            temp = temp.sort_values(by="res", ascending=True)
            return temp
        
        elif order == "RMBSAnnualNI":
            return self.runRMBSStatsEngine(groupBy=["PRICING YEAR",'Subsector'], filter={})
        

        elif order == "PerformingLoanIssuer":
            return self.runRMBSStatsEngine(
                groupBy=["Shelf"],
                filter={
                    "Subsector": ["Performing"],
                    "PRICING YEAR": self._latestYears,
                },
            ).sort_values(by="res", ascending=False)
        
        elif order == "CRTLoanIssuer":
            return self.runRMBSStatsEngine(
                groupBy=["Shelf"],
                filter={
                    "Subsector": ["CRT"],
                    "PRICING YEAR": self._latestYears,
                },
            ).sort_values(by="res", ascending=False)
        
        elif order == "PrimeJumboLoanIssuer":
            return self.runRMBSStatsEngine(
                groupBy=["Shelf"],
                filter={
                    "Subsector": ["PrimeJumbo"],
                    "PRICING YEAR": self._latestYears,
                },
            ).sort_values(by="res", ascending=False)

        elif order == "performingBBBSpread":
            return self.runRMBSSectorSpread(ratings=["BBB"], subsector=["Performing"])
        
        elif order == "crtBBBSpread":
            return self.runRMBSSectorSpread(ratings=["BBB"], subsector=["CRT"])
        
        elif order == "primejumboBBBSpread":
            return self.runRMBSSectorSpread(ratings=["BBB"], subsector=["PrimeJumbo"])

        elif order == "performingBBSpread":
            return self.runRMBSSectorSpread(ratings=["BB"], subsector=["Performing"])
        
        elif order == "crtBBSpread":
            return self.runRMBSSectorSpread(ratings=["BB"], subsector=["CRT"])
        
        elif order == "primejumboBBSpread":
            return self.runRMBSSectorSpread(ratings=["BB"], subsector=["PrimeJumbo"])

        elif order == "performingBB_BBBSpread":
            return self.runRmbsBB_BBB_Spread('Performing')
        
        elif order == "crtBB_BBBSpread":
            return self.runRmbsBB_BBB_Spread('CRT')
        
        elif order == "primejumboBB_BBBSpread":
            return self.runRmbsBB_BBB_Spread('PrimeJumbo')
        