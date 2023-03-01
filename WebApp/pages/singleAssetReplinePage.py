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

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


from app import app, db_mgr
from app import Asset, AssetRamper, SPCFUtils


assetReplineSnapshot = db_mgr.load_assetRepline()
assetReplineSnapshot = assetReplineSnapshot.sort_values(
    by=["replineIndex"], ascending=True
)

layout = html.Div(
    [
        html.H4(id="datatable-title", children="Asset Repline"),
        html.Button("Load Selected", id="load-select-repline", n_clicks=0),
        html.Button("Refresh", id="refresh-repline-table", n_clicks=0),
        html.Br(),
        dash_table.DataTable(
            id="repline-table",
            columns=[
                {"name": i, "id": i, "deletable": True, "selectable": True}
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
        html.Div(
            id="asset-repline-pad1",
            children=[
                html.Div(
                    id="repline-terms-inputs",
                    children=[
                        html.I("Notional"),
                        html.Br(),
                        dcc.Input(
                            id="notional-input",
                            type="text",
                            placeholder="",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        html.I("Term"),
                        html.Br(),
                        dcc.Input(
                            id="term-input",
                            type="text",
                            placeholder="",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        html.I("IntRate"),
                        html.Br(),
                        dcc.Input(
                            id="intrate-input",
                            type="text",
                            placeholder="",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        html.I("CDRVector"),
                        html.Br(),
                        dcc.Input(
                            id="cdrvector-input",
                            type="text",
                            placeholder="",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        html.I("CPRVector"),
                        html.Br(),
                        dcc.Input(
                            id="cprvector-input",
                            type="text",
                            placeholder="",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        html.I("SEVVector"),
                        html.Br(),
                        dcc.Input(
                            id="sevvector-input",
                            type="text",
                            placeholder="",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        html.I("DQVector"),
                        html.Br(),
                        dcc.Input(
                            id="dqvector-input",
                            type="text",
                            placeholder="",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        html.Button(
                            "Run Cashflow", id="run-single-repline-cashflow", n_clicks=0
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
    [
        State("notional-input", "value"),
        State("term-input", "value"),
        State("intrate-input", "value"),
        State("cdrvector-input", "value"),
        State("cprvector-input", "value"),
        State("sevvector-input", "value"),
        State("dqvector-input", "value"),
        Input("run-single-repline-cashflow", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def run_specific_repline(
    notionalInput,
    termInput,
    intrateInput,
    cdrvectorInput,
    cprvectorInput,
    sevvectorInput,
    dqvectorInput,
    n_clicks,
):

    notionalFloat = float(notionalInput)
    termInt = int(termInput)
    intrateFloat = float(intrateInput)

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

    liveRepline = Asset.AmortizationAsset(
        notional=notionalFloat,
        term=termInt,
        intRate=intrateFloat,
        cdrVector=cdrvectorList,
        cprVector=cprvectorList,
        sevVector=sevvectorList,
        dqVector=dqvectorList,
    )

    liveCF = liveRepline.cashflow
    liveYieldtable = liveRepline.calculateYieldTable(
        pxList=[90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]
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
    [
        Output("notional-input", "value"),
        Output("term-input", "value"),
        Output("intrate-input", "value"),
        Output("cdrvector-input", "value"),
        Output("cprvector-input", "value"),
        Output("sevvector-input", "value"),
        Output("dqvector-input", "value"),
    ],
    [
        State("repline-table", "data"),
        State("repline-table", "selected_rows"),
        Input("load-select-repline", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def load_repline_assumption(rows, selected_rows, n_clicks):
    if selected_rows is None:
        return ["", "", "", "", "", "", ""]

    if len(selected_rows) == 0:
        return ["", "", "", "", "", "", ""]

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
    ]
