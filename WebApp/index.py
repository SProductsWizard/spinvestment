import dash
import plotly
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output


import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import plotly.express as px

from app import app
from pages import singleAssetReplinePage, rampAssetPage, warehousePage

server = app.server
controlDropdownList = [
    "Single Asset Repline",
    "Ramp Manager",
    "Warehouse",
]

app.layout = html.Div(
    [
        html.Div("SPCF", id="header"),
        dcc.Dropdown(
            id="control-dropdown",
            options=[{"label": item, "value": item} for item in controlDropdownList],
            # value=controlDropdownList[0],
            value="Warehouse",
        ),
        html.Div(id="page-content"),
    ]
)


@app.callback(Output("page-content", "children"), [Input("control-dropdown", "value")])
def display_page(pageValue):
    if pageValue == "Single Asset Repline":
        return singleAssetReplinePage.layout
    elif pageValue == "Ramp Manager":
        return rampAssetPage.layout
    elif pageValue == "Warehouse":
        return warehousePage.layout
    else:
        return "To be Developed"


if __name__ == "__main__":
    app.run_server(debug=True)
