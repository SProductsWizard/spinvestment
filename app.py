import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

app = dash.Dash(__name__)
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
            value="Warehouse",
        ),
        html.Div(id="page-content"),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
