from dash import html, dcc

import dash
from WebApp.pages import masterPage

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
                    children=masterPage.layout,
                    style=dict(width="10%"),
                ),
                html.Hr(),
                html.Div(
                    id="main-content-right-canvas",
                    style=dict(width="90%"),
                    children=[
                        html.Div(
                            id="main-content-right-upper-canvas",
                            children=masterPage.subMenu,
                        ),
                        html.Div(
                            id="main-content-right-lower-canvas",
                            children=masterPage.content,
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
