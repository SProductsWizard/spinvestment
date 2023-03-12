from dash import dcc, html, callback


from plotly.subplots import make_subplots

from Utils.FigureFactory import FiguerFactory
from WebApp.appBackendResources import *


row1Fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "Consumer Loan Annual NI",
        "Top 15 Consumer Loan Shelf",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    row1Fig, figFactoryEngine.figures["ConsumerLoanAnnualVolume"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    row1Fig, figFactoryEngine.figures["ConsumerLoanIssuer"], row=1, col=2
)

#
row2Fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "Consumer Loan BBB and BB Spread",
        "BB / BBB Spread (Credit Curve)",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    row2Fig, figFactoryEngine.figures["consumerLoanBBSpread_Scatter"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    row2Fig, figFactoryEngine.figures["consumerLoanBBBSpread_Scatter"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    row2Fig,
    figFactoryEngine.figures["consumerLoanBB/BBBSpread_Scatter"],
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
