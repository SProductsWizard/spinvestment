from dash import dcc, html, dash_table, callback
import plotly.graph_objs as go
import plotly.express as px

from dash.dependencies import Input, Output, State


import WebApp.gadgetsUtil.gadetsGroup as gadetsGroup
from WebApp.appBackendResources import *


assetReplineSnapshot = db_mgr.load_assetRepline()
rampPoolSnapshot = db_mgr.load_rampPool()

pageTitle = "warehousePage"
assetInputsGadgets = gadetsGroup.AssetInputsGadetsGroup(pageTitle=pageTitle)
rampInputsGadgets = gadetsGroup.RampInputsGadgetsGroup(pageTitle=pageTitle)

layout = html.Div(
    [
        html.H4(children="Warehouse Modeling Input"),
        html.Br(),
        html.Div(
            id="warehouse-modeling-input",
            children=[
                html.Div(
                    id="warehouse-modeling-asset-input",
                    children=[
                        html.I("Asset Modeling Input"),
                        html.Div(
                            id="warehouse-modeling-asset-input-content",
                            children=assetInputsGadgets.layout,
                        ),
                    ],
                    style=dict(width="20%"),
                ),
                html.Div(
                    id="warehouse-modeling-ramp-input",
                    children=[
                        html.I("Ramp Modeling Input"),
                        html.Div(
                            id="warehouse-modeling-ramp-input-content",
                            children=rampInputsGadgets.layout,
                        ),
                    ],
                    style=dict(width="20%"),
                ),
                html.Div(
                    id="warehouse-modeling-wh-input",
                    children=[
                        html.I("Warehouse Terms Modeling Input"),
                        html.Div(
                            id="warehouse-modeling-wh-input-content",
                            children=gadetsGroup.warehouseInputsGroup(pageTitle),
                        ),
                    ],
                    style=dict(width="60%"),
                ),
            ],
            style=dict(display="flex"),
        ),
        html.Hr(),
        html.H4(children="Warehouse Run Results"),
        html.Button(
            "Run Warehouse",
            id="run-warehouse",
            n_clicks=0,
            style={"background-color": "#FFF8DC"},
        ),
        html.Div(
            id="warehouse-run-results-output",
            children=[
                html.Div(
                    children=[
                        html.I("Warehouse Levered Economics Stats"),
                        html.Div(
                            id="warehouse-eco-stats-content",
                        ),
                    ],
                    style=dict(width="25%"),
                ),
                html.Div(
                    children=[
                        html.I("Warehouse Econoimcs Illustration"),
                        html.Div(
                            id="warehouse-eco-illustration-content",
                            children=[
                                html.Div(
                                    style=dict(height="50%"),
                                    children=[
                                        html.Div(
                                            id="warehouse-chart1",
                                        ),
                                        html.Div(
                                            id="warehouse-chart2",
                                        ),
                                    ],
                                ),
                                html.Div(
                                    style=dict(height="50%"),
                                    children=[
                                        html.Div(
                                            id="warehouse-chart3",
                                        ),
                                        html.Div(
                                            id="warehouse-chart4",
                                        ),
                                    ],
                                ),
                            ],
                            style=dict(display="flex"),
                        ),
                    ],
                    style=dict(width="75%"),
                ),
            ],
            style=dict(display="flex"),
        ),
    ]
)


@callback(
    [
        Output("warehouse-eco-stats-content", "children"),
        Output("warehouse-chart1", "children"),
        Output("warehouse-chart2", "children"),
        Output("warehouse-chart3", "children"),
        Output("warehouse-chart4", "children"),
    ],
    assetInputsGadgets.getState()
    + rampInputsGadgets.getState()
    + [
        State(f"{pageTitle}-warehouse-commit-period-input", "value"),
        State(f"{pageTitle}-warehouse-tranch-terms-input", "data"),
        State(f"{pageTitle}-warehouse-fee-dollar-input", "data"),
        State(f"{pageTitle}-warehouse-fee-ratios-input", "data"),
        Input("run-warehouse", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def run_warehouse(
    assetNotionalInput,
    assetTermInput,
    assetIntrateInput,
    assetCdrvectorInput,
    assetCprvectorInput,
    assetSevvectorInput,
    assetDqvectorInput,
    assetServicingfeesInput,
    rampCommitPeriodInput,
    rampSizeVectorInput,
    rampPxVectorInput,
    warehouseCommitPeriodInput,
    warehouseTrancheTermsInput,
    warehouseFeeDollarInput,
    warehouseFeeRatiosInput,
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

    rampCommitPeriod = int(SPCFUtils.SPCFUtils.convertStrFloat(rampCommitPeriodInput))
    rampSizeVector = SPCFUtils.SPCFUtils.convertIntexRamp(
        rampSizeVectorInput, rampCommitPeriod, divisor=1 / 1e6
    )
    rampPxVector = SPCFUtils.SPCFUtils.convertIntexRamp(
        rampPxVectorInput, rampCommitPeriod
    )

    warehouseWhTerms = {}
    warehouseWhTerms["commitDetails"] = {
        "period": int(SPCFUtils.SPCFUtils.convertStrFloat(warehouseCommitPeriodInput))
    }
    warehouseWhTerms["advRate"] = dict(
        [
            (item["Tranche"], SPCFUtils.SPCFUtils.convertStrFloat(item["advRate"]))
            for item in warehouseTrancheTermsInput
        ]
    )
    warehouseWhTerms["coupon"] = dict(
        [
            (item["Tranche"], SPCFUtils.SPCFUtils.convertStrFloat(item["coupon"]))
            for item in warehouseTrancheTermsInput
        ]
    )
    warehouseWhTerms["undrawnFee"] = dict(
        [
            (item["Tranche"], SPCFUtils.SPCFUtils.convertStrFloat(item["undrawnFee"]))
            for item in warehouseTrancheTermsInput
        ]
    )
    warehouseWhTerms["facilitySize"] = dict(
        [
            (item["Tranche"], SPCFUtils.SPCFUtils.convertStrFloat(item["facilitySize"]))
            for item in warehouseTrancheTermsInput
        ]
    )
    warehouseWhTerms["transactionFees"] = {}
    warehouseWhTerms["transactionFees"]["feeDollars"] = dict(
        [
            (k, SPCFUtils.SPCFUtils.convertStrFloat(v))
            for k, v in warehouseFeeDollarInput[0].items()
        ]
    )

    warehouseWhTerms["transactionFees"]["feeRatios"] = dict(
        [
            (k, SPCFUtils.SPCFUtils.convertStrFloat(v))
            for k, v in warehouseFeeRatiosInput[0].items()
        ]
    )

    amAsset = Asset.AmortizationAsset(
        notional=assetNotional,
        term=assetTerm,
        intRate=assetIntrate,
        cdrVector=assetCdrvector,
        cprVector=assetCprvector,
        sevVector=assetSevvector,
        dqVector=assetDqvector,
        servicingFeesRatio=assetServicingfees,
    )
    assetRamperMgr = AssetRamper.AssetRamper(
        sizeList=rampSizeVector, pxList=rampPxVector, assetList=[amAsset]
    )
    warehouseMgr = Warehouse.WarehouseStructure(
        rampPool=assetRamperMgr, whTerms=warehouseWhTerms, exitDetails={}
    )

    warehouseEcoStatsTable = warehouseMgr.formatWarehouseEcoStats

    temp1 = warehouseMgr.warehouseStats["ts_metrics"]["balances"].reset_index()
    temp1.columns = ["_".join(col) for col in temp1.columns]
    temp1["rampPeriod_"] = temp1["rampPeriod_"].apply(str)

    temp2 = warehouseMgr.warehouseStats["ts_metrics"]["effectiveAdv"].reset_index()
    temp2.columns = ["_".join(col) for col in temp2.columns]

    temp3 = warehouseMgr.warehouseStats["ts_metrics"]["cashDistribution"].reset_index()
    temp3.columns = ["_".join(col) for col in temp3.columns]

    temp4 = warehouseMgr.warehouseStats["ts_metrics"][
        "cashDistributionGranular"
    ].reset_index()
    temp4.columns = ["_".join(col) for col in temp4.columns]

    figBal = px.bar(
        temp1,
        y=[
            item
            for item in list(temp1.columns)
            if item not in ["rampPeriod_", "Asset_eopBal"]
        ],
        x="rampPeriod_",
        barmode="stack",
        title="Asset and Debt Balacnes",
    )
    figBal.add_traces(
        go.Scatter(
            x=temp1["rampPeriod_"],
            y=temp1["Asset_eopBal"],
            name="Asset_eopBal",
            mode="lines+markers+text",
            showlegend=True,
        )
    )

    figAdv = px.line(
        temp2,
        y=[item for item in list(temp2.columns) if item != "rampPeriod_"],
        x="rampPeriod_",
        title="Effective Advance Rate",
    )

    figCashdistribution = px.bar(
        temp3,
        y=[
            item
            for item in list(temp3.columns[::-1])
            if item not in ["rampPeriod_", "Asset_repaymentCash"]
        ],
        x="rampPeriod_",
        barmode="stack",
        title="Cash Distribution",
    )
    figCashdistribution.add_traces(
        go.Scatter(
            x=temp3["rampPeriod_"],
            y=temp3["Asset_repaymentCash"],
            name="Asset_repaymentCash",
            mode="lines+markers+text",
            showlegend=True,
        )
    )

    figCashdistributionGranular = px.bar(
        temp4,
        y=[
            item
            for item in list(temp4.columns[::-1])
            if item not in ["rampPeriod_", "Asset_repaymentCash"]
        ],
        x="rampPeriod_",
        barmode="stack",
        title="Cash Distribution Granularity",
    )
    figCashdistributionGranular.add_traces(
        go.Scatter(
            x=temp4["rampPeriod_"],
            y=temp4["Asset_repaymentCash"],
            name="Asset_repaymentCash",
            mode="lines+markers+text",
            showlegend=True,
        )
    )

    return [
        dash_table.DataTable(
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": True}
                for i in warehouseEcoStatsTable.columns
            ],
            data=warehouseEcoStatsTable.to_dict("records"),
            editable=True,
        ),
        dcc.Graph(figure=figBal),
        dcc.Graph(figure=figAdv),
        dcc.Graph(figure=figCashdistribution),
        dcc.Graph(figure=figCashdistributionGranular),
    ]
