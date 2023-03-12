from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from WebApp.appBackendResources import *
from datetime import date


df = db_mgr.finsightDataStatus()
res = go.Figure(
    data=[
        go.Table(
            header=dict(
                values=list(df.columns),
                fill_color="paleturquoise",
                align="left",
            ),
            cells=dict(
                values=[df[[col]] for col in df.columns],
                fill_color="lavender",
                align="left",
            ),
        )
    ]
)


layout = html.Div([dcc.Graph(figure=res)])
