from dash import dcc, html, callback
from plotly.subplots import make_subplots

from Utils.FigureFactory import FiguerFactory
from WebApp.appBackendResources import *

#this is really nonprime
row1Fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "RMBS NQM Annual NI",
        "Top 10 NQM Loan Shelf",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    row1Fig, figFactoryEngine.figures["rmbsAnnualVolume_Performing"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    row1Fig, figFactoryEngine.figures["PerformingLoanIssuer"], row=1, col=2
)

#
row2Fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "RMBS NQM  BBB and BB Spread",
        "BB / BBB Spread (Credit Curve)",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    row2Fig, figFactoryEngine.figures["performingBBSpread_Scatter"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    row2Fig, figFactoryEngine.figures["performingBBBSpread_Scatter"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    row2Fig,
    figFactoryEngine.figures["performingBB/BBBSpread_Scatter"],
    row=1,
    col=2,
)
row2Fig.data[0].marker.color = "red"
row2Fig.update_layout(showlegend=True)

layout = html.Div(
    [
        dcc.Graph(figure=row1Fig),
        dcc.Graph(figure=row2Fig),
    ]
)
