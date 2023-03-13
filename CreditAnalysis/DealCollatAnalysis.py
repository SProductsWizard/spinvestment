import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta
from DatabaseManagement.db_driver import AtlasDriver
from Utils.SPCFUtils import SPCFUtils
import re
from plotly.subplots import make_subplots
import random
import plotly.graph_objects as go


class DealCollatAnalysis:
    def __init__(self):
        print("******************* Load DealCollatAnalysis *******************")
        self.atlasDriver = AtlasDriver(readOnly=True)
        self.rawData = {}
        self._loadData()
        self._cleanData()
        self._tagData()
        self._standardizeData()
        self.liveVintageFigs = []
        self.sectorTrackingFigs = {}
        self.sectorMetricsLastValue = {}
        print("******************* Load DealCollatAnalysis Done *******************")

    def _loadData(self):
        self.rawData["ABSStats"] = self.atlasDriver.load_data("ItxCollatStats")
        self.rawData["ABSDeals"] = self.atlasDriver.load_data("ItxDeals")
        self.rawData["ABSTranches"] = self.atlasDriver.load_data("ItxTranches")

    def _cleanData(self):
        absStatsDf = self.rawData["ABSStats"]
        absDealsDf = self.rawData["ABSDeals"]
        absTranchesDf = self.rawData["ABSTranches"]

        # lower case deal name column
        absStatsDf["DealName"] = absStatsDf["DealName"].str.lower()
        absDealsDf["DealName"] = absDealsDf["DealName"].str.lower()
        absTranchesDf["DealName"] = absTranchesDf["DealName"].str.lower()

        # convert datefiels from string to datetime for DealsDf
        absDealsDf["FirstPayDate"] = pd.to_datetime(absDealsDf["FirstPayDate"])
        absDealsDf["ClosingDate"] = pd.to_datetime(absDealsDf["ClosingDate"])

        # convert string to double for numeric fields
        for col in [
            item
            for item in list(absStatsDf.columns)
            if item not in ["DealName", "LatestUpdate"]
        ]:
            absStatsDf[col] = absStatsDf[col].apply(
                lambda x: np.nan
                if x in ["NULL", "-"]
                else float(str(x).replace(",", ""))
            )

        # convert LatestUpdate from datetime to date
        absStatsDf["LatestUpdate"] = pd.to_datetime(absStatsDf["LatestUpdate"])
        absStatsDf["AsofMonth"] = absStatsDf["LatestUpdate"].dt.to_period("M")
        absStatsDf["LatestUpdate"] = absStatsDf["LatestUpdate"].dt.date

        # marry up stats and deals tables so that deals info can be used on stats
        absStatsDf = absStatsDf.merge(
            absDealsDf[
                ["DealName", "ClosingDate", "FirstPayDate", "CollatType", "DealType"]
            ],
            on="DealName",
            how="left",
        )

        # create new columns: MOB, Factor
        absStatsDf.loc[:, "MOB"] = absStatsDf.apply(
            lambda x: (relativedelta(x["LatestUpdate"], x["FirstPayDate"]).years * 12)
            + (relativedelta(x["LatestUpdate"], x["FirstPayDate"]).months + 1),
            axis=1,
        )
        absStatsDf.loc[absStatsDf["MOB"] < 0, "MOB"] = 0

        absStatsDf.loc[:, "Factor"] = (
            absStatsDf.loc[:, "CurrBal"] / absStatsDf.loc[:, "OrigBal"]
        )

        # create new columns: LtL
        absStatsDf.loc[:, "LtL"] = absStatsDf.loc[:, "AccumNetLossPct"] / (
            1 - absStatsDf.loc[:, "Factor"]
        )

        # generate Lag varialbes: MOB, delinquencies
        absStatsDf = absStatsDf.sort_values(by=["DealName", "LatestUpdate", "MOB"])
        absStatsDf["MOB_Lag1"] = absStatsDf.groupby("DealName")["MOB"].shift(1)
        absStatsDf["MOB_Lag2"] = absStatsDf.groupby("DealName")["MOB"].shift(2)
        absStatsDf["MOB_Lag3"] = absStatsDf.groupby("DealName")["MOB"].shift(3)

        absStatsDf[
            ["1moDelinq90Plus_lag1", "Del6089_lag1", "Del3059_lag1"]
        ] = absStatsDf.groupby("DealName")[
            ["1moDelinq90Plus", "Del6089", "Del3059"]
        ].shift(
            1
        )
        absStatsDf[["1moDelinq60Plus_lag2", "Del6089_lag2"]] = absStatsDf.groupby(
            "DealName"
        )[["1moDelinq60Plus", "Del6089"]].shift(2)
        absStatsDf[["1moDelinq30Plus_lag3", "Del3059_lag3"]] = absStatsDf.groupby(
            "DealName"
        )[["1moDelinq30Plus", "Del3059"]].shift(3)

        self.rawData["ABSStats"] = absStatsDf
        self.rawData["ABSDeals"] = absDealsDf
        self.rawData["ABSTranches"] = absTranchesDf

    def _tagData(self):
        absStatsDf = self.rawData["ABSStats"]
        cond1 = lambda x: absStatsDf["DealName"].str.startswith(x)
        cond2 = (absStatsDf["DealType"] == "CONSUMER") & (
            absStatsDf["CollatType"].isin(
                ["Personal Loans", "Marketplace:  Personal Loans"]
            )
        )

        cond3 = (absStatsDf["DealType"] == "AUTOLOAN") & (
            absStatsDf["CollatType"] == "Subprime"
        )

        cond4 = (absStatsDf["DealType"] == "EQUIPMENT") & (
            absStatsDf["CollatType"] == "Large Ticket"
        )

        absStatsDf.loc[:, "IssuerTag"] = ""
        absStatsDf.loc[:, "IssuerSubTag"] = ""
        absStatsDf.loc[:, "SectorTag"] = ""
        absStatsDf.loc[:, "SectorSubTag"] = ""

        absStatsDf.loc[cond2, "SectorTag"] = "consumerLoan"
        absStatsDf.loc[cond3, "SectorTag"] = "subprimeAuto"
        absStatsDf.loc[cond4, "SectorTag"] = "largeTicket"

        absStatsDf.loc[cond1("upst") & cond2, "IssuerTag"] = "upstart"
        absStatsDf.loc[cond1("upsp") & cond2, "IssuerTag"] = "upstart"
        absStatsDf.loc[cond1("uspt") & cond2, "IssuerTag"] = "upstart"
        absStatsDf.loc[cond1("free") & cond2, "IssuerTag"] = "freedom"
        absStatsDf.loc[cond1("ldp") & cond2, "IssuerTag"] = "lendingPoint"
        absStatsDf.loc[cond1("lpf") & cond2, "IssuerTag"] = "lendingPoint"
        absStatsDf.loc[cond1("lpp") & cond2, "IssuerTag"] = "lendingPoint"
        absStatsDf.loc[cond1("paid") & cond2, "IssuerTag"] = "pagaya"
        absStatsDf.loc[cond1("pmit") & cond2, "IssuerTag"] = "prosper"
        absStatsDf.loc[cond1("prsp") & cond2, "IssuerTag"] = "prosper"
        absStatsDf.loc[cond1("ump") & cond2, "IssuerTag"] = "upgrade"
        absStatsDf.loc[cond1("urpt") & cond2, "IssuerTag"] = "upgrade"
        absStatsDf.loc[cond1("umc") & cond2, "IssuerTag"] = "upgrade"
        absStatsDf.loc[cond1("upgr") & cond2, "IssuerTag"] = "upgrade"
        absStatsDf.loc[cond1("thrm") & cond2, "IssuerTag"] = "theorem"

        absStatsDf.loc[cond1("sdar") & cond3, "IssuerTag"] = "santander"
        absStatsDf.loc[cond1("wlrt") & cond3, "IssuerTag"] = "westlake"
        absStatsDf.loc[cond1("exar") & cond3, "IssuerTag"] = "exeter"
        absStatsDf.loc[cond1("acar") & cond3, "IssuerTag"] = "gm"
        absStatsDf.loc[cond1("acac") & cond3, "IssuerTag"] = "acar"
        absStatsDf.loc[cond1("dtat") & cond3, "IssuerTag"] = "drivetime"
        absStatsDf.loc[cond1("glsa") & cond3, "IssuerTag"] = "gls"
        absStatsDf.loc[cond1("flgc") & cond3, "IssuerTag"] = "flagship"
        absStatsDf.loc[cond1("cpsa") & cond3, "IssuerTag"] = "cps"
        absStatsDf.loc[cond1("cvar") & cond3, "IssuerTag"] = "carvana"
        absStatsDf.loc[cond1("cpsa") & cond3, "IssuerTag"] = "cps"

        # accumulative bond volume "market share" by issuer. top 10 covers >82%

        # Banco Santander SA                  0.288080
        # Hankey Group                        0.409096
        # Exeter Finance                      0.509714
        # General Motors Co                   0.591047
        # American Credit Acceptance          0.637396
        # DriveTime Automotive Group Inc      0.680794
        # Global Lending Services LLC         0.722693
        # Flagship Credit Acceptance          0.764338
        # Carvana Group LLC                   0.796040
        # Consumer Portfolio Services Inc     0.827274

        absStatsDf.loc[cond1("nmeq") & cond4, "IssuerTag"] = "northMill"

        self.rawData["ABSStats"] = absStatsDf

    def _standardizeData(self):
        absStatsDf = self.rawData["ABSStats"]
        absStatsDf.rename(
            columns={
                "LatestUpdate": "AsofDate",
            },
            inplace=True,
        )

        self.rawData["ABSStats"] = absStatsDf[
            [
                "DealName",
                "AsofDate",
                "AsofMonth",
                "OrigBal",
                "CurrBal",
                "Factor",
                "GrossCpn",
                "NetCpn",
                "AmortTerm",
                "RemTerm",
                "WALA",
                "NumOfAssets",
                "CPR1M",
                "CPR3M",
                "CPR6M",
                "CPR12M",
                "CPRLife",
                "CDR1M",
                "CDR3M",
                "CDR6M",
                "CDR12M",
                "CDRLife",
                "CRR1M",
                "CRR3M",
                "CRR6M",
                "CRR12M",
                "CRRLife",
                "SEV1M",
                "SEV3M",
                "SEV6M",
                "SEV12M",
                "SEVLife",
                "AnnNetLoss",
                "AccumNetLossPct",
                "AccumNetLoss",
                "LtL",
                "Del3059",
                "Del6089",
                "1moDelinq30Plus",
                "1moDelinq60Plus",
                "1moDelinq90Plus",
                "1moPrinRepurch",
                "1moPrinRecovery",
                "1moIntCollected",
                "1moPrnCollected",
                "ClosingDate",
                "FirstPayDate",
                "CollatType",
                "DealType",
                "MOB",
                "MOB_Lag1",
                "MOB_Lag2",
                "MOB_Lag3",
                "1moDelinq90Plus_lag1",
                "Del6089_lag1",
                "Del3059_lag1",
                "1moDelinq60Plus_lag2",
                "Del6089_lag2",
                "1moDelinq30Plus_lag3",
                "Del3059_lag3",
                "IssuerTag",
                "IssuerSubTag",
                "SectorTag",
            ]
        ]

    def sectorTracking(
        self,
        sector,
        minDate="2017-11",
        minMOB=4,
        issuerExclude=[],
        issuerInclude=[],
        excludePeriods=[],
    ):
        if len(issuerExclude) * len(issuerInclude) > 0:
            raise Exception("either specify exclude or include; cannot specify both")

        absStatsDf = self.rawData["ABSStats"]
        absStatsDf = absStatsDf[absStatsDf["SectorTag"] == sector]

        absStatsDf = absStatsDf[absStatsDf["MOB"] >= minMOB]
        absStatsDf = absStatsDf[
            absStatsDf["AsofDate"] >= datetime.strptime(minDate, "%Y-%m").date()
        ]

        if len(issuerExclude) > 0:
            absStatsDf = absStatsDf[~(absStatsDf["IssuerTag"].isin(issuerExclude))]

        if len(issuerInclude) > 0:
            absStatsDf = absStatsDf[absStatsDf["IssuerTag"].isin(issuerInclude)]

        absStatsDf = absStatsDf[~(absStatsDf["IssuerTag"] == "")]

        weights = lambda x: SPCFUtils.weightAvg(x, absStatsDf, "CurrBal")

        stats = (
            absStatsDf.groupby(["AsofMonth"])
            .agg(
                DealCnt=("DealName", "count"),
                WALA=("WALA", weights),
                CDR=("CDR1M", weights),
                AnnualizedNetLoss=("AnnNetLoss", weights),
                SEV=("SEV1M", weights),
                DQ3059=("Del3059", weights),
                DQ6089=("Del6089", weights),
                DQ90P=("1moDelinq90Plus", weights),
                DQ30P=("1moDelinq30Plus", weights),
                MOB=("MOB", weights),
            )
            .reset_index()
        )

        issuerBreakdown = (
            absStatsDf[["CurrBal", "AsofMonth", "IssuerTag"]]
            .groupby(["AsofMonth", "IssuerTag"])
            .agg(BalAgg=("CurrBal", "sum"))
            .reset_index()
        )

        issuerBreakdown.loc[:, "IssuerPct"] = issuerBreakdown[
            "BalAgg"
        ] / issuerBreakdown.groupby(["AsofMonth"])["BalAgg"].transform("sum")

        issuerBreakdownPivot = issuerBreakdown.pivot(
            index="AsofMonth", columns="IssuerTag", values="IssuerPct"
        )

        if len(excludePeriods) > 0:
            stats.loc[
                stats["AsofMonth"].isin(excludePeriods),
                [item for item in stats.columns if item != "AsofMonth"],
            ] = np.NaN

            issuerBreakdownPivot = issuerBreakdownPivot.reset_index()
            issuerBreakdownPivot.loc[
                issuerBreakdownPivot["AsofMonth"].isin(excludePeriods),
                [item for item in issuerBreakdownPivot.columns if item != "AsofMonth"],
            ] = np.NaN
            issuerBreakdownPivot = issuerBreakdownPivot.set_index("AsofMonth")

            issuerBreakdown.loc[
                issuerBreakdown["AsofMonth"].isin(excludePeriods),
                [item for item in issuerBreakdown.columns if item != "AsofMonth"],
            ] = np.NaN

        # adjust AsofMonth column for plotly graph

        stats.loc[:, "AsofMonth"] = (
            stats.loc[:, "AsofMonth"].apply(lambda x: x.to_timestamp()).dt.normalize()
        )

        issuerBreakdown.loc[:, "AsofMonth"] = (
            issuerBreakdown.loc[:, "AsofMonth"]
            .apply(lambda x: x.to_timestamp())
            .dt.normalize()
        )

        self.sectorTrackingRes = {
            "trakcingStats": stats,
            "issuerBreakdownPivot": issuerBreakdownPivot,
            "issuerBreakdown": issuerBreakdown,
        }
        return self

    def showSectorTrackingStats(self, resKey):
        # resKey:
        # "trakcingStats"
        # "issuerBreakdownPivot"
        # "issuerBreakdown"

        print(self.sectorTrackingRes[resKey])

        return self

    def sectorTrackingDraft(self):
        self.sectorTrackingFigs = {}
        self.sectorMetricsLastValue = {}

        trackingStats = self.sectorTrackingRes["trakcingStats"]

        issuerBreakdown = self.sectorTrackingRes["issuerBreakdown"]

        self.sectorTrackingFigs["WALA"] = px.line(
            trackingStats[["AsofMonth", "WALA"]], x="AsofMonth", y="WALA"
        )
        self.sectorTrackingFigs["DealCnt"] = px.line(
            trackingStats[["AsofMonth", "DealCnt"]], x="AsofMonth", y="DealCnt"
        )

        self.sectorTrackingFigs["IssuerBreakdown"] = px.area(
            issuerBreakdown[["AsofMonth", "IssuerTag", "IssuerPct"]],
            y="IssuerPct",
            x="AsofMonth",
            color="IssuerTag",
        )
        self.sectorTrackingFigs["IssuerBreakdown"].update_layout(yaxis_ticksuffix="%")

        for creditMetric in [
            "CDR",
            "AnnualizedNetLoss",
            "DQ3059",
            "DQ6089",
            "DQ90P",
            "DQ30P",
        ]:
            self.sectorTrackingFigs[creditMetric] = px.line(
                trackingStats[["AsofMonth", creditMetric]],
                x="AsofMonth",
                y=creditMetric,
            )
            self.sectorTrackingFigs[creditMetric].update_traces(mode="markers+lines")
            self.sectorMetricsLastValue[creditMetric] = trackingStats[
                [creditMetric]
            ].values[-1][0]

        return self

    # def plotSectorTracking(self):
    #     trackingStats = self.sectorTrackingRes["trakcingStats"]
    #     issuerBreakdown = self.sectorTrackingRes["issuerBreakdown"]

    #     fig, axs = plt.subplots(3, 6, figsize=(21, 10))
    #     trackingStats[["AsofMonth", "WALA"]].plot(
    #         "AsofMonth",
    #         "WALA",
    #         kind="line",
    #         ax=axs[0, 0],
    #         xlabel="",
    #         markersize=3,
    #         marker="o",
    #         markerfacecolor="none",
    #         title="WALA",
    #     )

    #     trackingStats[["AsofMonth", "DealCnt"]].plot(
    #         "AsofMonth",
    #         "DealCnt",
    #         kind="line",
    #         ax=axs[0, 1],
    #         xlabel="",
    #         markersize=3,
    #         marker="o",
    #         markerfacecolor="none",
    #         title="Deal Count",
    #     )

    #     issuerBreakdown[["AsofMonth", "IssuerTag", "IssuerPct"]].groupby(
    #         ["AsofMonth", "IssuerTag"]
    #     ).sum().unstack().plot(
    #         kind="area",
    #         stacked=True,
    #         ax=axs[0, 2],
    #         xlabel="",
    #         title="Issuer Balance Percentage",
    #     )

    #     axs[0, 2].legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)

    #     for idx, col in enumerate(
    #         ["CDR", "AnnualizedNetLoss", "DQ3059", "DQ6089", "DQ90P", "DQ30P"]
    #     ):
    #         trackingStats[["AsofMonth", col]].plot(
    #             "AsofMonth",
    #             col,
    #             kind="line",
    #             ax=axs[1, idx],
    #             xlabel="",
    #             markersize=3,
    #             marker="o",
    #             markerfacecolor="none",
    #             title=col,
    #         )

    #         sns.histplot(
    #             data=trackingStats[[col]],
    #             ax=axs[2, idx],
    #             bins=50,
    #             kde=True,
    #         ).set(title=f"{col} histogram")

    #         axs[2, idx].plot(
    #             [trackingStats[col].tail(1).values[0]] * 2,
    #             [0, axs[2, idx].get_ylim()[1]],
    #             color="red",
    #             linestyle="dashed",
    #         )

    #     fig.delaxes(axs[0, 3])
    #     fig.delaxes(axs[0, 4])
    #     fig.delaxes(axs[0, 5])

    #     plt.show()
    #     return self

    def vintageTracking(self, **kwargs):
        # cusipList = kwargs.get('cusipList')
        shelfList = kwargs.get("shelfList")
        dealList = kwargs.get("dealList")
        # issuerList = kwargs.get('issuerList')
        includeYearVintage = kwargs.get("includeYearVintage")
        excludeYearVintgae = kwargs.get("excludeYearVintgae")
        minYearVintage = kwargs.get("minYearVintage")

        if (not includeYearVintage == None) & (not excludeYearVintgae == None):
            raise Exception(
                "either specify includeYearVintage or excludeYearVintgae; cannot specify both"
            )

        absStatsDf = self.rawData["ABSStats"]
        if not minYearVintage == None:
            absStatsDf = absStatsDf[absStatsDf["ClosingDate"].dt.year >= minYearVintage]

        if not includeYearVintage == None:
            absStatsDf = absStatsDf[
                absStatsDf["ClosingDate"].dt.year.isin(includeYearVintage)
            ]

        if not excludeYearVintgae == None:
            absStatsDf = absStatsDf[
                ~(absStatsDf["ClosingDate"].dt.year.isin(excludeYearVintgae))
            ]

        if not dealList == None:
            absStatsDf = absStatsDf[absStatsDf["DealName"].isin(dealList)]

        cond = np.logical_or.reduce(
            [absStatsDf["DealName"].str.startswith(shelf) for shelf in shelfList]
        )

        absStatsDf = absStatsDf[cond][
            [
                "MOB",
                "DealName",
                "CDR1M",
                "Del3059",
                "Del6089",
                "1moDelinq90Plus",
                "SEV1M",
                "AccumNetLossPct",
                "LtL",
            ]
        ]
        absStatsDf.loc[:, "Shelf"] = absStatsDf["DealName"].str.extract(
            "([a-zA-Z ]*)\d*.*"
        )
        self.vintageRes = {"vintageCurves": absStatsDf}

        return self

    def vintageCurvesDraft(self):
        self.liveVintageFigs = []
        vintageCurves = self.vintageRes["vintageCurves"]
        shelfList = list(vintageCurves["Shelf"].unique())
        shelfCnt = len(shelfList)
        r = lambda: random.randint(0, 255)
        colorSchemes = {
            item: ("#%02X%02X%02X" % (r(), r(), r()))
            for item in vintageCurves["DealName"].unique()
        }

        # CDR, CPR, CNL, SEV, 3060, 6089, 90+, Loss to Liquidation
        fig = make_subplots(
            rows=shelfCnt,
            cols=7,
            subplot_titles=[
                "CDR",
                "DQ30",
                "DQ60",
                "DQ90+",
                "SEV",
                "CNL",
                "Loss to Liquidation",
            ]
            * shelfCnt,
        )

        for shelfIdx, shelf in enumerate(shelfList):
            shelfVintageCurves = vintageCurves[vintageCurves["Shelf"] == shelf]
            for metrixIdx, metrix in enumerate(
                [
                    "CDR1M",
                    "Del3059",
                    "Del6089",
                    "1moDelinq90Plus",
                    "SEV1M",
                    "AccumNetLossPct",
                    "LtL",
                ]
            ):
                shelfVintageCurvesPivot = shelfVintageCurves.pivot_table(
                    index="MOB", columns="DealName", values=metrix, aggfunc="mean"
                ).reset_index(drop=False)

                for col in [
                    item for item in shelfVintageCurvesPivot.columns if item != "MOB"
                ]:
                    fig.add_trace(
                        go.Scatter(
                            x=shelfVintageCurvesPivot["MOB"],
                            y=shelfVintageCurvesPivot[col],
                            name=col,
                            legendgroup=col,
                            line_color=colorSchemes[col],
                            showlegend=(True if metrixIdx == 0 else False),
                        ),
                        row=shelfIdx + 1,
                        col=metrixIdx + 1,
                    )

        fig.update_xaxes(title_text="MOB")
        fig.update_layout(height=shelfCnt * 350, width=350 * 7)
        self.liveVintageFigs += [fig]
        return self

    def vintageDisplayTweak(self, **kwargs):
        dealList = kwargs.get("dealList")
        regexPattern = kwargs.get("regexPattern")

        if not dealList == None:
            self.liveVintageFigs[0].for_each_trace(
                lambda trace: trace.update(opacity=1)
                if trace.name in dealList
                else trace.update(opacity=0)
            )
            return self

        if not regexPattern == None:
            self.liveVintageFigs[0].for_each_trace(
                lambda trace: trace.update(opacity=1)
                if bool(re.findall(regexPattern, trace.name))
                else trace.update(opacity=0)
            )
            return self

        return self

    def showVintageCurves(self):
        for vintageFig in self.liveVintageFigs:
            vintageFig.show()
        return self
