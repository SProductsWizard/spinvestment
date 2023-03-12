from dash import html, dcc

import dash
from WebApp.pages import menuPage

app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True


app.layout = html.Div(
    [
        html.H1("Structured Products Investment Tookit", id="header"),
        html.Div(
            id="main-content-canvas",
            children=[
                html.Div(
                    id="main-content-left-canvas",
                    children=menuPage.layout,
                    style=dict(width="20%"),
                ),
                html.Hr(),
                html.Div(
                    id="main-content-right-canvas",
                    style=dict(width="80%"),
                    children=[
                        html.Div(
                            id="main-content-right-upper-canvas",
                            children=menuPage.subMenu,
                        ),
                        html.Div(
                            id="main-content-right-lower-canvas",
                            children=menuPage.content,
                        ),
                    ],
                ),
            ],
            style=dict(display="flex"),
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
