from dash import dcc, html, callback
from plotly.subplots import make_subplots

from Utils.FigureFactory import FiguerFactory

from WebApp.appBackendResources import *

dealCollatsEngine.vintageTracking(
    shelfList=["upst"], dealList=["upst181", "upst191", "upst221"]
).vintageCurvesDraft()


layout = html.Div([dcc.Graph(figure=dealCollatsEngine.liveVintageFigs[0])])
