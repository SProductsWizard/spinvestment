from dash import dcc, html, callback
from plotly.subplots import make_subplots

from Utils.FigureFactory import FiguerFactory
from WebApp.appBackendResources import *

#this is really nonprime
row1Fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "RMBS Prime Jumbo Annual NI",
        "Top 10 2.0 Loan Shelf",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    row1Fig, figFactoryEngine.figures["rmbsAnnualVolume_PrimeJumbo"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    row1Fig, figFactoryEngine.figures["PrimeJumboLoanIssuer"], row=1, col=2
)

#
row2Fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "RMBS Nonprime  BBB and BB Spread",
        "BB / BBB Spread (Credit Curve)",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    row2Fig, figFactoryEngine.figures["primejumboBBSpread_Scatter"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    row2Fig, figFactoryEngine.figures["primejumboBBBSpread_Scatter"], row=1, col=1
)

#TODO: Fix PrimeJumbo spread chart
FiguerFactory.insertPlotlypxToSubplot(
    row2Fig,
    figFactoryEngine.figures["crtBB/BBBSpread_Scatter"],
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
