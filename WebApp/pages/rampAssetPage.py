import dash_core_components as dcc
import dash_html_components as html
from dash import dash_table
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
from dash.dependencies import Input, Output, State
import pandas as pd
from copy import deepcopy

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


from app import app, db_mgr
from app import Asset, AssetRamper, SPCFUtils


assetReplineSnapshot = db_mgr.load_assetRepline()
rampPoolSnapshot = db_mgr.load_rampPool()


layout = html.Div(
    [
        html.H4(children="Asset Repline"),
        html.Br(),
        html.Div(
            id="repline-table-div2",
            children=[
                dash_table.DataTable(
                    id="repline-table2",
                    columns=[
                        {"name": i, "id": i, "deletable": False, "selectable": True}
                        for i in assetReplineSnapshot.columns
                    ],
                    data=assetReplineSnapshot.to_dict("records"),
                    sort_mode="single",
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                ),
            ],
        ),
        html.Br(),
        html.H4(children="Ramp Pool"),
        html.Div(
            id="ramp-table-div",
            children=[
                dash_table.DataTable(
                    id="ramp-table",
                    columns=[
                        {"name": i, "id": i, "deletable": False, "selectable": True}
                        for i in rampPoolSnapshot.columns
                    ],
                    data=rampPoolSnapshot.to_dict("records"),
                    sort_mode="single",
                    row_selectable="single",
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                ),
            ],
        ),
        html.Div(
            id="ramp-pool-pad1",
            children=[
                html.Div(
                    id="ramp-pool-inputs",
                    children=[
                        html.I("Ramp Pool Inputs"),
                        html.Br(),
                        html.I("Commit Period"),
                        html.Br(),
                        dcc.Input(
                            id="commit-period-input",
                            type="text",
                            placeholder="",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        html.Br(),
                        html.I("Repline Vector"),
                        html.Br(),
                        dcc.Input(
                            id="repline-vector-input",
                            type="text",
                            placeholder="",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        html.Br(),
                        html.I("Size Vector (mm)"),
                        html.Br(),
                        dcc.Input(
                            id="size-vector-input",
                            type="text",
                            placeholder="",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        html.Br(),
                        html.I("Px Vector"),
                        html.Br(),
                        dcc.Input(
                            id="px-vector-input",
                            type="text",
                            placeholder="",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        html.Br(),
                        html.Button("Load Selected", id="load-select-ramp", n_clicks=0),
                        html.Br(),
                        html.Br(),
                        html.Button("Run Cashflow", id="run-ramp-cashflow", n_clicks=0),
                        html.Br(),
                        html.Br(),
                        html.Button(
                            "Add to Database",
                            id="add-new-ramp-to-database",
                            n_clicks=0,
                        ),
                    ],
                    style=dict(width="10%"),
                ),
                html.Div(
                    id="single-ramp-display1",
                    children=[
                        html.Div("Ramp Pool Cashflow Table"),
                        html.Div(id="ramp-pool-cashflowtable"),
                    ],
                    style=dict(width="90%"),
                ),
            ],
            style=dict(display="flex"),
        ),
        html.Div(
            id="ramp-pool-pad2",
            children=[
                html.Div(
                    id="ramp-static-metrics",
                    children=[
                        html.I("Ramp Pool Matrics"),
                        html.Div(id="ramp-static-metrics-content"),
                    ],
                    style=dict(width="20%"),
                ),
                html.Div(
                    id="collat-static-metrics",
                    children=[
                        html.I("Ramp Portfolio Performance"),
                        html.Div(
                            id="ramp-portfolio-performance-charts-div",
                            children=[
                                html.Div(id="ramp-portfolio-performance-chart1-div"),
                                html.Div(id="ramp-portfolio-performance-chart2-div"),
                                html.Div(id="ramp-portfolio-performance-chart3-div"),
                                html.Div(id="ramp-portfolio-performance-chart4-div"),
                            ],
                        ),
                    ],
                    style=dict(width="80%"),
                ),
            ],
            style=dict(display="flex"),
        ),
    ]
)


@app.callback(
    [
        Output("repline-vector-input", "value"),
        Output("size-vector-input", "value"),
        Output("px-vector-input", "value"),
        Output("commit-period-input", "value"),
    ],
    [
        State("ramp-table", "data"),
        State("ramp-table", "selected_rows"),
        Input("load-select-ramp", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def load_ramp_assumptions(rows, selected_rows, n_clicks):
    if selected_rows is None:
        return ["", "", "", ""]

    if len(selected_rows) == 0:
        return ["", "", "", ""]

    selectId = selected_rows[0]
    selectContent = rows[selectId]

    return [
        selectContent["replineVector"],
        selectContent["sizeVector"],
        selectContent["pxVector"],
        selectContent["commitPeriod"],
    ]


@app.callback(
    [
        Output("ramp-pool-cashflowtable", "children"),
        Output("ramp-static-metrics-content", "children"),
        Output("ramp-portfolio-performance-chart1-div", "children"),
        Output("ramp-portfolio-performance-chart2-div", "children"),
        Output("ramp-portfolio-performance-chart3-div", "children"),
        Output("ramp-portfolio-performance-chart4-div", "children"),
    ],
    [
        State("repline-vector-input", "value"),
        State("size-vector-input", "value"),
        State("px-vector-input", "value"),
        State("commit-period-input", "value"),
        Input("run-ramp-cashflow", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def run_specific_ramp(
    replineVector_input,
    sizeVector_input,
    pxVector_input,
    commitPeriod_input,
    n_clicks,
):
    global assetReplineSnapshot
    commitPeriodInt = int(commitPeriod_input)
    replineVectorList = SPCFUtils.SPCFUtils.convertIntexRamp(
        intexSyntax=replineVector_input, term=commitPeriodInt, divisor=1, forceInt=True
    )
    pxVectorList = SPCFUtils.SPCFUtils.convertIntexRamp(
        intexSyntax=pxVector_input, term=commitPeriodInt, divisor=1
    )
    sizeVectorList = SPCFUtils.SPCFUtils.convertIntexRamp(
        intexSyntax=sizeVector_input, term=commitPeriodInt, divisor=1 / 1e6
    )

    # this should be optimized. load list of asset repline
    assetList = []
    assetReplineSnapshot = db_mgr.load_assetRepline()
    for replineIndex in replineVectorList:
        replineInput = assetReplineSnapshot[
            assetReplineSnapshot["replineIndex"] == str(replineIndex)
        ]
        notionalInput = replineInput["notional"].values[0]
        termInput = replineInput["term"].values[0]
        intrateInput = replineInput["intRate"].values[0]

        notionalFloat = float(notionalInput)
        termInt = int(termInput)
        intrateFloat = float(intrateInput)

        cdrvectorInput = replineInput["cdrVector"].values[0]
        cprvectorInput = replineInput["cprVector"].values[0]
        sevvectorInput = replineInput["sevVector"].values[0]
        dqvectorInput = replineInput["dqVector"].values[0]

        cdrvectorList = SPCFUtils.SPCFUtils.convertIntexRamp(
            intexSyntax=cdrvectorInput, term=termInt, divisor=100
        )
        cprvectorList = SPCFUtils.SPCFUtils.convertIntexRamp(
            intexSyntax=cprvectorInput, term=termInt, divisor=100
        )
        sevvectorList = SPCFUtils.SPCFUtils.convertIntexRamp(
            intexSyntax=sevvectorInput, term=termInt, divisor=100
        )
        dqvectorList = SPCFUtils.SPCFUtils.convertIntexRamp(
            intexSyntax=dqvectorInput, term=termInt, divisor=100
        )
        replineInstance = Asset.AmortizationAsset(
            notional=notionalFloat,
            term=termInt,
            intRate=intrateFloat,
            cdrVector=cdrvectorList,
            cprVector=cprvectorList,
            sevVector=sevvectorList,
            dqVector=dqvectorList,
        )
        assetList.append(deepcopy(replineInstance))

    assetRamperMgr = AssetRamper.AssetRamper(
        sizeList=sizeVectorList, pxList=pxVectorList, assetList=assetList
    )

    return [
        dash_table.DataTable(
            columns=[
                {"name": i, "id": i, "deletable": True, "selectable": True}
                for i in assetRamperMgr.rampCashflow.columns
            ],
            data=assetRamperMgr.rampCashflow.to_dict("records"),
            sort_mode="single",
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=10,
            style_table={"overflowY": "scroll"},
        ),
        dash_table.DataTable(
            columns=[
                {"name": i, "id": i, "deletable": True, "selectable": True}
                for i in assetRamperMgr.getStaticMetrics().columns
            ],
            data=assetRamperMgr.getStaticMetrics().to_dict("records"),
            sort_mode="single",
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=20,
            style_table={"overflowY": "scroll"},
        ),
        dcc.Graph(
            figure=px.line(
                assetRamperMgr.rampStats["ts_metrics"]["investmentCFCurve"],
                y="cumulativeInvestmentCash",
                x="rampPeriod",
            )
        ),
        dcc.Graph(
            figure=px.line(
                assetRamperMgr.rampStats["ts_metrics"]["portfolioBalanceCurve"],
                y="bopBal",
                x="rampPeriod",
            )
        ),
        dcc.Graph(
            figure=px.line(
                assetRamperMgr.rampStats["ts_metrics"]["repaymentCurve"],
                y=["netIntCF", "prinCF"],
                x="rampPeriod",
            )
        ),
        dcc.Graph(
            figure=px.line(
                assetRamperMgr.rampStats["ts_metrics"]["dollarLossCurve"],
                y="cumulativeLossPrin",
                x="rampPeriod",
            )
        ),
    ]
