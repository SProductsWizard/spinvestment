from dash import dcc, html, callback
from plotly.subplots import make_subplots

from Utils.FigureFactory import FiguerFactory

from WebApp.appBackendResources import *


volumeFig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "ABS NI Volume",
        # "2021 / 2022 NI By Subsector",
        "ABS NI Year Vintage Comp",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    volumeFig, figFactoryEngine.figures["ABSNIAnnualVolume"], row=1, col=1
)

# FiguerFactory.insertPlotlypxToSubplot(
#     volumeFig, figFactoryEngine.figures["ABSNI2022/2021Subsector"], row=1, col=2
# )

FiguerFactory.insertPlotlypxToSubplot(
    volumeFig, figFactoryEngine.figures["ABSNIVintage"], row=1, col=2
)

volumeFig.update_layout(yaxis2=dict(tickfont=dict(size=10)))
volumeFig.update_layout(height=600)

# Row 2 Charts

volumeRatingsFig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "Below IG (BB/B/NR) NI Avg Annual Amount",
        "IG (A/BBB) NI Avg Annual Amount",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    volumeRatingsFig, figFactoryEngine.figures["ABSNISubsectorSubIG"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    volumeRatingsFig,
    figFactoryEngine.figures["ABSNISubsectorBelowAAIG"],
    row=1,
    col=2,
)

volumeRatingsFig.update_layout(
    yaxis=dict(tickfont=dict(size=10)), yaxis2=dict(tickfont=dict(size=10))
)

volumeRatingsFig.update_layout(height=600)

# Row 3 Charts

spreadFig = make_subplots(
    rows=1,
    cols=3,
    subplot_titles=(
        "Subprime Auto BBB Spread (Benchmark ABS BBB) vs. CDX IG",
        "Subprime Auto BB Spread (Benchmark ABS BB) vs. CDX HY",
        "Latest Rel Val",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    spreadFig,
    figFactoryEngine.figures["subprimeAutoBBBSpread_Scatter"],
    row=1,
    col=1,
)

FiguerFactory.insertPlotlypxToSubplot(
    spreadFig, figFactoryEngine.figures["subprimeAutoBBSpread_Scatter"], row=1, col=2
)

FiguerFactory.insertPlotlypxToSubplot(
    spreadFig,
    figFactoryEngine.figures["LatestRelVal"],
    row=1,
    col=3,
)


layout = html.Div(
    [
        figFactoryEngine.figures["ABSNIBondTable"],
        dcc.Graph(figure=spreadFig),
        dcc.Graph(figure=volumeFig),
        dcc.Graph(figure=volumeRatingsFig),
    ]
)
