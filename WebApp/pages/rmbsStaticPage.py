from dash import dcc, html, callback, dash_table
from plotly.subplots import make_subplots

from Utils.FigureFactory import FiguerFactory

from WebApp.appBackendResources import *
 
import pandas as pd
from pathlib import Path
import os
# to do: for now data is saved as pickle. will update after we discuss database migration

path = Path(__file__).parent.absolute()
severity_table=pd.read_pickle(os.path.join(path,'severity.pkl'))


layout = html.Div(
    html.Div(
            children=[
                html.Div("CRT Severity By Origination"),
                dash_table.DataTable(
                    id="severity-table",
                    columns=[
                        {"name": i, "id": i, "deletable": True} for i in severity_table.columns
                    ],
                    data=severity_table.to_dict("records"),
                    filter_action="native",
                    sort_action="native",
                    sort_mode="single",
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                ),
            ]
        )


)
