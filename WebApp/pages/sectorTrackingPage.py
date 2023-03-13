from dash import dcc, html, callback, Input, Output

from plotly.subplots import make_subplots

from Utils.FigureFactory import FiguerFactory

from WebApp.appBackendResources import *

assetClasses = ["subprimeAuto", "consumerLoan"]
dealStats = ["WALA", "DealCnt", "IssuerBreakdown"]
creditMetrics = ["CDR", "AnnualizedNetLoss", "DQ3059", "DQ6089", "DQ90P", "DQ30P"]

layout = html.Div(
    [
        dcc.Dropdown(
            assetClasses,
            assetClasses[0],
            id="sector-tracking-assetclass-dropdown",
            style={"color": "#3D59AB", "font-size": 20},
        ),
        html.Div(id="sector-tracking-content-div"),
    ]
)


@callback(
    Output("sector-tracking-content-div", "children"),
    Input("sector-tracking-assetclass-dropdown", "value"),
)
def showSectorTracking(value):
    dealCollatsEngine.sectorTracking(
        sector=value, minDate="2018-05"
    ).sectorTrackingDraft()

    dealStatsFig = make_subplots(rows=1, cols=3, subplot_titles=dealStats)

    for idx, item in enumerate(dealStats):
        FiguerFactory.insertPlotlypxToSubplot(
            dealStatsFig,
            dealCollatsEngine.sectorTrackingFigs[item],
            row=1,
            col=idx + 1,
        )
    dealStatsFig.update_layout(yaxis3_tickformat=",.0%")

    creditMetrixFig = make_subplots(
        rows=1,
        cols=6,
        subplot_titles=creditMetrics,
    )

    for idx, creditMetric in enumerate(creditMetrics):
        FiguerFactory.insertPlotlypxToSubplot(
            creditMetrixFig,
            dealCollatsEngine.sectorTrackingFigs[creditMetric],
            row=1,
            col=idx + 1,
        )
        creditMetrixFig.add_hline(
            y=dealCollatsEngine.sectorMetricsLastValue[creditMetric],
            row=1,
            col=idx + 1,
            line_dash="dot",
            line_color="red",
        )

    return html.Div([dcc.Graph(figure=dealStatsFig), dcc.Graph(figure=creditMetrixFig)])
