from dash import dcc, html, dash_table
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd

from spcashflow.WebApp.appResources import *

import spcashflow.WebApp.pages.gadetsGroup as gadetsGroup

assetReplineSnapshot = db_mgr.load_assetRepline()
pageTitle = "singleAssetRepline"
assetInputsGadgets = gadetsGroup.AssetInputsGadetsGroup(pageTitle=pageTitle)

layout = html.Div(
    [
        html.H4(children="Asset Repline"),
        html.Br(),
        html.Div(
            id="repline-table-div",
            children=[
                dash_table.DataTable(
                    id="repline-table",
                    columns=[
                        {"name": i, "id": i, "deletable": False, "selectable": True}
                        for i in assetReplineSnapshot.columns
                    ],
                    data=assetReplineSnapshot.to_dict("records"),
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
            id="asset-repline-pad1",
            children=[
                html.Div(
                    id="repline-terms-inputs",
                    children=[
                        html.I("Asset Modeling Input"),
                        html.Div(
                            id="repline-modeling-asset-input-content",
                            children=assetInputsGadgets.layout,
                        ),
                        html.Br(),
                        html.Br(),
                        html.Button(
                            "Load Selected", id="load-select-repline", n_clicks=0
                        ),
                        html.Br(),
                        html.Br(),
                        html.Button(
                            "Run Cashflow", id="run-single-repline-cashflow", n_clicks=0
                        ),
                        html.Br(),
                        html.Br(),
                        html.Button(
                            "Add to Database",
                            id="add-new-repline-to-database",
                            n_clicks=0,
                        ),
                    ],
                    style=dict(width="10%"),
                ),
                html.Div(
                    id="single-repline-display1",
                    children=[
                        html.Div("Cashflow Table"),
                        html.Div(id="single-repline-cashflowtable"),
                    ],
                    style=dict(width="90%"),
                ),
            ],
            style=dict(display="flex"),
        ),
        html.Div(
            id="asset-repline-pad2",
            children=[
                html.Div(
                    id="yield-table-div",
                    children=[
                        html.I("Yield Table"),
                        html.Div(id="yield-table-content"),
                    ],
                    style=dict(width="50%"),
                ),
                html.Div(
                    id="collat-static-metrics",
                    children=[
                        html.I("Collat Matrics"),
                        html.Div(id="collat-static-metrics-content"),
                    ],
                    style=dict(width="50%"),
                ),
            ],
            style=dict(display="flex"),
        ),
        html.Div(
            id="asset-repline-pad3",
            children=[
                html.Div(
                    id="asset-ts-metrics-chart1-div",
                    children=[
                        html.I("CDR Curve"),
                        html.Div(id="cdr-curve-content"),
                    ],
                    style=dict(width="33%"),
                ),
                html.Div(
                    id="asset-ts-metrics-chart2-div",
                    children=[
                        html.I("CPR Curve"),
                        html.Div(id="cpr-curve-content"),
                    ],
                    style=dict(width="33%"),
                ),
                html.Div(
                    id="asset-ts-metrics-chart3-div",
                    children=[
                        html.I("SEV Curve"),
                        html.Div(id="sev-curve-content"),
                    ],
                    style=dict(width="34%"),
                ),
            ],
            style=dict(display="flex"),
        ),
        html.Div(
            id="asset-repline-pad4",
            children=[
                html.Div(
                    id="asset-ts-metrics-chart4-div",
                    children=[
                        html.I("DQ Curve"),
                        html.Div(id="dq-curve-content"),
                    ],
                    style=dict(width="33%"),
                ),
                html.Div(
                    id="asset-ts-metrics-chart5-div",
                    children=[
                        html.I("CNL Curve"),
                        html.Div(id="cnl-curve-content"),
                    ],
                    style=dict(width="33%"),
                ),
                html.Div(
                    id="asset-ts-metrics-chart6-div",
                    children=[
                        html.I("Factor Curve"),
                        html.Div(id="factor-curve-content"),
                    ],
                    style=dict(width="34%"),
                ),
            ],
            style=dict(display="flex"),
        ),
    ]
)


@app.callback(
    Output("repline-table-div", "children"),
    [
        State("notional-input", "value"),
        State("term-input", "value"),
        State("intrate-input", "value"),
        State("cdrvector-input", "value"),
        State("cprvector-input", "value"),
        State("sevvector-input", "value"),
        State("dqvector-input", "value"),
        State("servicingfees-input", "value"),
        Input("add-new-repline-to-database", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def add_new_repline(
    notionalInput,
    termInput,
    intrateInput,
    cdrvectorInput,
    cprvectorInput,
    sevvectorInput,
    dqvectorInput,
    servicingfeesInput,
    n_clicks,
):
    global assetReplineSnapshot
    newLine = {}
    newLine["replineIndex"] = str(int(assetReplineSnapshot["replineIndex"].max()) + 1)
    newLine["intRate"] = intrateInput
    newLine["notional"] = notionalInput
    newLine["term"] = termInput
    newLine["cdrVector"] = cdrvectorInput
    newLine["cprVector"] = cprvectorInput
    newLine["sevVector"] = sevvectorInput
    newLine["dqVector"] = dqvectorInput
    newLine["servicingfees"] = servicingfeesInput

    newLine["archive"] = "FALSE"
    newLine["replineType"] = "amortization"

    db_mgr.upload_assetRepline(pd.DataFrame([newLine]))

    assetReplineSnapshot = db_mgr.load_assetRepline()

    return (
        dash_table.DataTable(
            id="repline-table",
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": True}
                for i in assetReplineSnapshot.columns
            ],
            data=assetReplineSnapshot.to_dict("records"),
            sort_mode="single",
            row_selectable="single",
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=10,
        ),
    )


@app.callback(
    [
        Output("yield-table-content", "children"),
        Output("collat-static-metrics-content", "children"),
        Output("single-repline-cashflowtable", "children"),
        Output("cdr-curve-content", "children"),
        Output("cpr-curve-content", "children"),
        Output("sev-curve-content", "children"),
        Output("dq-curve-content", "children"),
        Output("cnl-curve-content", "children"),
        Output("factor-curve-content", "children"),
    ],
    assetInputsGadgets.getState() + [Input("run-single-repline-cashflow", "n_clicks")],
    prevent_initial_call=True,
)
def run_specific_repline(
    assetNotionalInput,
    assetTermInput,
    assetIntrateInput,
    assetCdrvectorInput,
    assetCprvectorInput,
    assetSevvectorInput,
    assetDqvectorInput,
    assetServicingfeesInput,
    n_clicks,
):

    assetNotional = SPCFUtils.SPCFUtils.convertStrFloat(assetNotionalInput)
    assetTerm = int(SPCFUtils.SPCFUtils.convertStrFloat(assetTermInput))
    assetIntrate = SPCFUtils.SPCFUtils.convertStrFloat(assetIntrateInput)
    assetCdrvector = SPCFUtils.SPCFUtils.convertIntexRamp(
        assetCdrvectorInput, assetTerm, divisor=100
    )
    assetCprvector = SPCFUtils.SPCFUtils.convertIntexRamp(
        assetCprvectorInput, assetTerm, divisor=100
    )
    assetSevvector = SPCFUtils.SPCFUtils.convertIntexRamp(
        assetSevvectorInput, assetTerm, divisor=100
    )
    assetDqvector = SPCFUtils.SPCFUtils.convertIntexRamp(
        assetDqvectorInput, assetTerm, divisor=100
    )
    assetServicingfees = SPCFUtils.SPCFUtils.convertStrFloat(assetServicingfeesInput)

    liveRepline = Asset.AmortizationAsset(
        notional=assetNotional,
        term=assetTerm,
        intRate=assetIntrate,
        cdrVector=assetCdrvector,
        cprVector=assetCprvector,
        sevVector=assetSevvector,
        dqVector=assetDqvector,
        servicingFeesRatio=assetServicingfees,
    )

    liveCF = liveRepline.cashflow
    liveYieldtable = liveRepline.calculateYieldTable(
        pxList=[91, 92, 93, 94, 95, 96, 97, 98, 99, 100]
    )
    liveCollatMetrics = liveRepline.getStaticMetrics()

    return [
        dash_table.DataTable(
            columns=[
                {"name": i, "id": i, "deletable": True, "selectable": True}
                for i in liveYieldtable.columns
            ],
            data=liveYieldtable.to_dict("records"),
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
                for i in liveCollatMetrics.columns
            ],
            data=liveCollatMetrics.to_dict("records"),
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
                for i in liveCF.columns
            ],
            data=liveCF.to_dict("records"),
            sort_mode="single",
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=10,
            style_table={"overflowY": "scroll"},
        ),
        dcc.Graph(
            figure=px.line(
                liveRepline.assetStats["ts_metrics"]["cdrCurve"],
                y="cdrVector",
                x="period",
            )
        ),
        dcc.Graph(
            figure=px.line(
                liveRepline.assetStats["ts_metrics"]["cprCurve"],
                y="cprVector",
                x="period",
            )
        ),
        dcc.Graph(
            figure=px.line(
                liveRepline.assetStats["ts_metrics"]["sevCurve"],
                y="sevVector",
                x="period",
            )
        ),
        dcc.Graph(
            figure=px.line(
                liveRepline.assetStats["ts_metrics"]["dqCurve"],
                y="dqVector",
                x="period",
            )
        ),
        dcc.Graph(
            figure=px.line(
                liveRepline.assetStats["ts_metrics"]["cnlCurve"],
                y=["cnl", "ltl"],
                x="period",
            )
        ),
        dcc.Graph(
            figure=px.line(
                liveRepline.assetStats["ts_metrics"]["factorCurve"],
                y="factor",
                x="period",
            )
        ),
    ]


@app.callback(
    assetInputsGadgets.getOutput(),
    [
        State("repline-table", "data"),
        State("repline-table", "selected_rows"),
        Input("load-select-repline", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def load_repline_assumption(rows, selected_rows, n_clicks):
    if selected_rows is None:
        return ["", "", "", "", "", "", "", ""]

    if len(selected_rows) == 0:
        return ["", "", "", "", "", "", "", ""]

    selectId = selected_rows[0]
    selectContent = rows[selectId]

    return [
        selectContent["notional"],
        selectContent["term"],
        selectContent["intRate"],
        selectContent["cdrVector"],
        selectContent["cprVector"],
        selectContent["sevVector"],
        selectContent["dqVector"],
        selectContent["servicingfees"],
    ]
