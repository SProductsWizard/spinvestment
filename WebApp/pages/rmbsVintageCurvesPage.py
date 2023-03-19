from dash import dcc, html, callback, Input, Output
from plotly.subplots import make_subplots

from Utils.FigureFactory import FiguerFactory

from WebApp.appBackendResources import *

import plotly.express as px
import pandas as pd
from pathlib import Path
import os
import pickle

# to do: for now data is saved as pickle. will update after we discuss database migration
path = Path(__file__).parent.absolute()

with open(os.path.join(path,'perf.pickle'), 'rb') as handle:
    perf_dict = pickle.load(handle)

def create_subplot(df,creditMetric):
        df=df.loc[df['Type'] == creditMetric].transpose()
        df.columns=df.iloc[0]
        df=df.iloc[2:]
            
        return px.line(
                df,
                x=df.index,
                y=df.columns,
            )

assetClasses = ['Low60', 'Low', 'High']
#dealStats = ["WALA", "DealCnt", "IssuerBreakdown"]
creditMetrics = ["Cum. Default along AXIS", "Cum. Net Loss along AXIS", "Cum. Prepay along AXIS", "SMM",'D60 Rate','D90+ Rate']

layout = html.Div(
    [
        dcc.Dropdown(
            assetClasses,
            assetClasses[0],
            id="rmbs-tracking-assetclass-dropdown",
            style={"color": "#3D59AB", "font-size": 20},
        ),
        html.Div(id="rmbs-tracking-content-div"),
    ]
)


@callback(
    Output("rmbs-tracking-content-div", "children"),
    Input("rmbs-tracking-assetclass-dropdown", "value"),
)
def showSectorTracking(value):

    df=perf_dict[value]

    creditMetrixFig = make_subplots(
        rows=1,
        cols=6,
        subplot_titles=creditMetrics,
    )

    for idx, creditMetric in enumerate(creditMetrics):
        FiguerFactory.insertPlotlypxToSubplot(
            creditMetrixFig,
            create_subplot(df,creditMetric),
            row=1,
            col=idx + 1,
        )

    return html.Div([dcc.Graph(figure=creditMetrixFig)])

