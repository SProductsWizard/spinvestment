from dash import dcc, dash_table, html
from pkg_resources import working_set
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime


class FiguerFactory:
    def __init__(self, backendHandle):
        self.backendHandle = backendHandle
        self.figures = {}

    @staticmethod
    def insertPlotlypxToSubplot(figH, plotlypxFig, row, col):
        for traces in [item for item in plotlypxFig["data"]]:
            figH.append_trace(traces, row=row, col=col)

    def createFigures(self):
        self.figures[""] = px.scatter(
            self.backendHandle.runPrecannedStats(order="").reset_index(),
            x="PRICING YEAR",
            y="res",
        )
        self.figures["cdxIG_Line"] = px.line(
            self.backendHandle.getCdxIG(), x="Date", y="CDX_IG"
        )
        self.figures["cdxIG_Line"].update_traces(line_color="#000000")

        self.figures["cdxHY_Line"] = px.line(
            self.backendHandle.getCdxHY(), x="Date", y="CDX_HY"
        )
        self.figures["cdxHY_Line"].update_traces(line_color="#DEB887")

        self.figures["subprimeAutoBBSpread_Scatter"] = px.scatter(
            self.backendHandle.runPrecannedStats(order="SubprimeAutoBBSpread")
            .reset_index()
            .rename(columns={"res": "BB"}),
            x="PRICING DATE",
            y="BB",
            title="Subprime Auto NI BB Spread",
        )
        self.figures["subprimeAutoBBSpread_Scatter"].add_traces(
            list(self.figures["cdxHY_Line"].select_traces())
        )

        self.figures["subprimeAutoBBBSpread_Scatter"] = px.scatter(
            self.backendHandle.runPrecannedStats(order="SubprimeAutoBBBSpread")
            .reset_index()
            .rename(columns={"res": "BBB"}),
            x="PRICING DATE",
            y="BBB",
            title="Subprime Auto NI BBB Spread",
        )
        self.figures["subprimeAutoBBBSpread_Scatter"].add_traces(
            list(self.figures["cdxIG_Line"].select_traces())
        )

        self.figures["consumerLoanBBSpread_Scatter"] = px.scatter(
            self.backendHandle.runPrecannedStats(order="ConsumerLoanBBSpread")
            .reset_index()
            .rename(columns={"res": "BB"}),
            x="PRICING DATE",
            y="BB",
            title="Consumer Loan NI BB Spread",
        )

        self.figures["consumerLoanBBBSpread_Scatter"] = px.scatter(
            self.backendHandle.runPrecannedStats(order="ConsumerLoanBBBSpread")
            .reset_index()
            .rename(columns={"res": "BBB"}),
            x="PRICING DATE",
            y="BBB",
            title="Consumer Loan NI BBB Spread",
        )

        self.figures["subprimeAutoBB/BBBSpread_Scatter"] = px.scatter(
            self.backendHandle.runPrecannedStats(
                order="SubprimeAutoBB_BBBSpread"
            ).reset_index(),
            x="PRICING DATE",
            y="res",
            title="Subprime Auto BB/BBB Spread Difference (Credit Curve)",
        )

        self.figures["consumerLoanBB/BBBSpread_Scatter"] = px.scatter(
            self.backendHandle.runPrecannedStats(
                order="ConsumerLoanBB_BBBSpread"
            ).reset_index(),
            x="PRICING DATE",
            y="res",
            title="Consumer Loan BB/BBB Spread Difference (Credit Curve)",
        )

        self.figures["ABSNIAnnualVolume"] = px.bar(
            self.backendHandle.runPrecannedStats(order="ABSAnnualNI").reset_index(),
            x="PRICING YEAR",
            y="res",
            title="ABS NI Volume",
        )

        self.figures["ABSNIVintage"] = px.line(
            self.backendHandle.runPrecannedStats(
                order="ABSNI202320222021Vintage"
            ).reset_index(),
            x="PRICING DAY OF YEAR",
            y=[2020, 2021, 2022, 2023],
            title="ABS NI Volume",
        )

        self.figures["ABSNISubsectorSubIG"] = px.bar(
            self.backendHandle.runPrecannedStats(
                order="ABSNISubsectorSubIG"
            ).reset_index(),
            x="res",
            y="Subsector",
            title="ABS NI Volume",
            orientation="h",
        )

        #resi
        self.figures["RMBSNISubsectorSubIG"] = px.bar(
            self.backendHandle.runPrecannedStats(
                order="RMBSNISubsectorSubIG"
            ).reset_index(),
            x="res",
            y="Subsector",
            title="RMBS NI Volume",
            orientation="h",
        )

        self.figures["ABSNISubsectorBelowAAIG"] = px.bar(
            self.backendHandle.runPrecannedStats(
                order="ABSNISubsectorBelowAAIG"
            ).reset_index(),
            x="res",
            y="Subsector",
            title="ABS NI Volume",
            orientation="h",
        )

        #resi
        self.figures["RMBSNISubsectorBelowAAIG"] = px.bar(
            self.backendHandle.runPrecannedStats(
                order="RMBSNISubsectorBelowAAIG"
            ).reset_index(),
            x="res",
            y="Subsector",
            title="RMBS NI Volume",
            orientation="h",
        )

        self.figures["ABSNI2022/2021Subsector"] = px.bar(
            self.backendHandle.runPrecannedStats(order="ABSNI20222021"),
            y="Subsector",
            x="res",
            color="PRICING YEAR",
            title="Long-Form Input",
            barmode="group",
            orientation="h",
        )

        self.figures["SubprimeAutoAnnualVolume"] = px.bar(
            self.backendHandle.runsubsectorVolume(
                subsector="subprimeAuto"
            ).reset_index(),
            x="PRICING YEAR",
            y="res",
            title="Subprime Auto Annual NI",
        )

        self.figures["SubprimeAutoIssuer"] = px.bar(
            self.backendHandle.runPrecannedStats("subprimeAutoIssuer")
            .sort_values(by="res", ascending=True)
            .reset_index()
            .tail(15),
            y="Shelf",
            x="res",
            orientation="h",
            title="Top 15 Subprime Auto Shelf",
        )

        self.figures["ConsumerLoanAnnualVolume"] = px.bar(
            self.backendHandle.runsubsectorVolume(
                subsector="consumerLoan"
            ).reset_index(),
            x="PRICING YEAR",
            y="res",
            title="Consumer Loan Annual NI",
        )

#resi RMBSAnnualVolume

        self.figures["RMBSAnnualVolume"] = px.bar(
            self.backendHandle.runPrecannedStats(order="RMBSAnnualNI").reset_index(),
            x="PRICING YEAR",
            y="res",
            color='Subsector',
            barmode = 'stack',
            title="RMBS New Issuance Volume By Sector",
        )

        self.figures["RMBSIVintage"] = px.line(
            self.backendHandle.runPrecannedStats(
                order="RMBSNI2023202220212020Vintage"
            ).reset_index(),
            x="PRICING DAY OF YEAR",
            y=[2020, 2021, 2022, 2023],
            title="RMBS NI Volume",
        )
        

        for subsector in ['Performing', 'CRT', 'PrimeJumbo']:
            self.figures["rmbsAnnualVolume_"+subsector] = px.bar(
                self.backendHandle.runsubsectorVolumeRMBS(
                    subsector=subsector#needs to be updated
                ).reset_index(),
                x="PRICING YEAR",
                y="res",
                title="RMBS 2.0 Annual NI(tbd)",
            )

            self.figures[fr"{subsector}LoanIssuer"] = px.bar(
                self.backendHandle.runPrecannedStats(fr"{subsector}LoanIssuer")
                .sort_values(by="res", ascending=True)
                .reset_index()
                .tail(15),
                y="Shelf",
                x="res",
                orientation="h",
                title=fr"Top 15 {subsector} Loan Shelf",
            )

#adding resi 

        for subsector in ['Performing', 'CRT', 'PrimeJumbo']:
            self.figures[fr"{subsector.lower()}BBSpread_Scatter"] = px.scatter(
                self.backendHandle.runPrecannedStats(order=fr"{subsector.lower()}BBSpread")
                .reset_index()
                .rename(columns={"res": "BB"}),
                x="PRICING DATE",
                y="BB",
                title=fr"{subsector} Loan NI BB Spread",
            )

            self.figures[fr"{subsector.lower()}BBBSpread_Scatter"] = px.scatter(
                self.backendHandle.runPrecannedStats(order=fr"{subsector.lower()}BBBSpread")
                .reset_index()
                .rename(columns={"res": "BBB"}),
                x="PRICING DATE",
                y="BBB",
                title=fr"{subsector} Loan NI BBB Spread",
            )

            try:
                self.figures[fr"{subsector.lower()}BB/BBBSpread_Scatter"] = px.scatter(
                    self.backendHandle.runPrecannedStats(
                        order=fr"{subsector.lower()}BB_BBBSpread"
                    ).reset_index(),
                    x="PRICING DATE",
                    y="res",
                    title=fr"{subsector} Loan BB/BBB Spread Difference (Credit Curve)",
                )
            except Exception as e:
                pass

        self.figures["ConsumerLoanIssuer"] = px.bar(
            self.backendHandle.runPrecannedStats("consumerLoanIssuer")
            .sort_values(by="res", ascending=True)
            .reset_index()
            .tail(15),
            y="Shelf",
            x="res",
            orientation="h",
            title="Top 15 Consumer Loan Shelf",
        )

        self.figures["LatestRelVal"] = px.scatter(
            self.backendHandle.runRelVal(numBackDays=30),
            y="Spread",
            x="WAL",
            color="LowestRatings",
            text="Subsector",
        )
        self.figures["LatestRelVal"].update_traces(textposition="bottom center")
        self.figures["LatestRelVal"].update_traces(marker={"size": 10})

        endDate = self.backendHandle.latestPricingDate - datetime.timedelta(180)
        self.figures["RelVal"] = px.scatter(
            self.backendHandle.runRelVal(numBackDays=30, endDate=endDate),
            y="Spread",
            x="WAL",
            color="LowestRatings",
            text="Subsector",
        )
        self.figures["RelVal"].update_traces(textposition="bottom center")
        self.figures["RelVal"].update_traces(marker={"size": 10})
        self.figures["RelVal"].update_layout(
            title=f"{endDate} Rel Val",
        )


     #resi
        self.figures["RMBSLatestRelVal"] = px.scatter(
            self.backendHandle.runRMBSRelVal(numBackDays=90),
            y="Spread",
            x="WAL",
            color="LowestRatings",
            text="Subsector",
        )
        # self.figures["RMBSLatestRelVal"].update_traces(textposition="bottom center")
        # self.figures["RMBSLatestRelVal"].update_traces(marker={"size": 10})   

        df = self.backendHandle.databaseStatus()
        self.figures["databaseStatus"] = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=list(df.columns),
                        fill_color="paleturquoise",
                        align="left",
                    ),
                    cells=dict(
                        values=[df[["index"]], df[["res"]]],
                        fill_color="lavender",
                        align="left",
                    ),
                )
            ]
        )

        df = self.backendHandle.getDisplayDf(500)
        self.figures["ABSNIBondTable"] = html.Div(
            children=[
                html.Div("ABS New Issue Bond"),
                dash_table.DataTable(
                    id="repline-table",
                    columns=[
                        {"name": i, "id": i, "deletable": True} for i in df.columns
                    ],
                    data=df.to_dict("records"),
                    filter_action="native",
                    sort_action="native",
                    sort_mode="single",
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                ),
            ]
        )


# --------------------------------------
# legace work
# how to make figure from go
# --------------------------------------
# spreadFig.add_trace(
#     go.Scatter(
#         x=bbbSpread["PRICING DATE"],
#         y=bbbSpread["res"],
#         mode="markers",
#         showlegend=False,
#     ),
#     row=1,
#     col=1,
# )
