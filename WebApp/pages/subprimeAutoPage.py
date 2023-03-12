from dash import dcc, html

from plotly.subplots import make_subplots

from Utils.FigureFactory import FiguerFactory

from WebApp.appBackendResources import *

row1Fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "Subprime Auto Annual NI",
        "Top 15 Subprime Auto Shelf",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    row1Fig, figFactoryEngine.figures["SubprimeAutoAnnualVolume"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    row1Fig, figFactoryEngine.figures["SubprimeAutoIssuer"], row=1, col=2
)

#
row2Fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "Subprime Auto BBB and BB Spread",
        "BB / BBB Spread (Credit Curve)",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    row2Fig, figFactoryEngine.figures["subprimeAutoBBSpread_Scatter"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    row2Fig, figFactoryEngine.figures["subprimeAutoBBBSpread_Scatter"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    row2Fig,
    figFactoryEngine.figures["subprimeAutoBB/BBBSpread_Scatter"],
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


# def create_layout(app, figEngineHandle):
#     # Page Layouts
#     #
#     row1Fig = make_subplots(
#         rows=1,
#         cols=2,
#         subplot_titles=(
#             "Subprime Auto Annual NI",
#             "Top 15 Subprime Auto Shelf",
#         ),
#     )

#     FiguerFactory.insertPlotlypxToSubplot(
#         row1Fig, figEngineHandle.figures["SubprimeAutoAnnualVolume"], row=1, col=1
#     )

#     FiguerFactory.insertPlotlypxToSubplot(
#         row1Fig, figEngineHandle.figures["SubprimeAutoIssuer"], row=1, col=2
#     )

#     #
#     row2Fig = make_subplots(
#         rows=1,
#         cols=2,
#         subplot_titles=(
#             "Subprime Auto BBB and BB Spread",
#             "BB / BBB Spread (Credit Curve)",
#         ),
#     )

#     FiguerFactory.insertPlotlypxToSubplot(
#         row2Fig, figEngineHandle.figures["subprimeAutoBBSpread_Scatter"], row=1, col=1
#     )

#     FiguerFactory.insertPlotlypxToSubplot(
#         row2Fig, figEngineHandle.figures["subprimeAutoBBBSpread_Scatter"], row=1, col=1
#     )

#     FiguerFactory.insertPlotlypxToSubplot(
#         row2Fig,
#         figEngineHandle.figures["subprimeAutoBB/BBBSpread_Scatter"],
#         row=1,
#         col=2,
#     )
#     row2Fig.data[0].marker.color = "red"
#     row2Fig.update_layout(showlegend=True)

#     return html.Div(
#         [
#             dcc.Graph(figure=row1Fig),
#             dcc.Graph(figure=row2Fig),
#         ]
#     )
