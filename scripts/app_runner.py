from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from spcashflow.WebApp.appResources import app
from spcashflow.WebApp.pages import singleAssetReplinePage, rampAssetPage, warehousePage


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