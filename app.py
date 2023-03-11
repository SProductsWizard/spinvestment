from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash

from WebApp.pages import singleAssetReplinePage, rampAssetPage, warehousePage


app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True

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
