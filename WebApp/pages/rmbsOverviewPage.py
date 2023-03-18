from dash import dcc, html, callback
from plotly.subplots import make_subplots

from Utils.FigureFactory import FiguerFactory

from WebApp.appBackendResources import *

## the merged data rmbsbond is us regions onlu

volumeFig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "RMBS New Issuance Volume By Sector",
        # "2021 / 2022 NI By Subsector",
        "RMBS New Issuance Year Vintage Comp",
    ),
)

FiguerFactory.insertPlotlypxToSubplot(
    volumeFig, figFactoryEngine.figures["RMBSAnnualVolume"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    volumeFig, figFactoryEngine.figures["RMBSIVintage"], row=1, col=2
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
    volumeRatingsFig, figFactoryEngine.figures["RMBSNISubsectorSubIG"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    volumeRatingsFig,
    figFactoryEngine.figures["RMBSNISubsectorBelowAAIG"],
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
    cols=2,
    subplot_titles=(
       # "Subprime Auto BBB Spread (Benchmark ABS BBB) vs. CDX IG",--placeholder
        "Subprime Auto BB Spread (Benchmark ABS BB) vs. CDX HY",
        "Latest Rel Val",
    ),
)
'''
FiguerFactory.insertPlotlypxToSubplot(
    spreadFig,
    figFactoryEngine.figures["subprimeAutoBBBSpread_Scatter"],
    row=1,
    col=1,
)
'''

FiguerFactory.insertPlotlypxToSubplot(
    spreadFig, figFactoryEngine.figures["subprimeAutoBBSpread_Scatter"], row=1, col=1
)

FiguerFactory.insertPlotlypxToSubplot(
    spreadFig,
    figFactoryEngine.figures["RMBSLatestRelVal"],
    row=1,
    col=2,
)


layout = html.Div(
    [
        figFactoryEngine.figures["ABSNIBondTable"],
        dcc.Graph(figure=spreadFig),
        dcc.Graph(figure=volumeFig),
        dcc.Graph(figure=volumeRatingsFig),
    ]
)
