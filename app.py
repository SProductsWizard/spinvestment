from dash import dcc
from dash import html

from dash.dependencies import Input, Output
import dash

# from WebApp.pages import menuPage, singleAssetReplinePage, rampAssetPage, warehousePage

from WebApp.pages import singleAssetReplinePage, rampAssetPage, warehousePage, menuPage

app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True

# menuList = [
#     "Public Market Dashboard",
#     "Credit Drill",
#     "Private Deal Maker",
#     "Reserch Hub",
#     "Street",
#     "SPWizard",
#     "Database Management",
# ]


# menuTabs = gadetsGroup.TabsGroup(
#     tabId="menuTabs", pageTitle="main", labelList=menuList, vertical=True
# )

controlDropdownList = [
    "Single Asset Repline",
    "Ramp Manager",
    "Warehouse",
]

app.layout = html.Div(
    [
        html.H1("Structured Products Investment Tookit", id="header"),
        # html.Div(
        #     id="main-content-canvas",
        #     children=[
        #         html.Div(
        #             id="main-content-left-canvas",
        #             children=menuPage.layout,
        #             style=dict(width="20%"),
        #         ),
        #         html.Hr(),
        #         html.Div(
        #             id="main-content-right-canvas",
        #             style=dict(width="80%"),
        #             children=[
        #                 html.Div(
        #                     id="main-content-right-upper-canvas",
        #                     children=menuPage.subMenu,
        #                 ),
        #                 html.Div(
        #                     id="main-content-right-lower-canvas",
        #                     children=menuPage.content,
        #                 ),
        #             ],
        #         ),
        #     ],
        #     style=dict(display="flex"),
        # ),
        # dcc.Dropdown(
        #     id="control-dropdown",
        #     options=[{"label": item, "value": item} for item in controlDropdownList],
        #     # value=controlDropdownList[0],
        #     value="Warehouse",
        # ),
        # html.Div(id="page-content"),
        # html.Div(children=menuTabs.layout),
    ]
)


# @app.callback(Output("page-content", "children"), [Input("control-dropdown", "value")])
# def display_page(pageValue):
#     if pageValue == "Single Asset Repline":
#         return singleAssetReplinePage.layout
#     elif pageValue == "Ramp Manager":
#         return rampAssetPage.layout
#     elif pageValue == "Warehouse":
#         return warehousePage.layout
#     else:
#         return "To be Developed"


if __name__ == "__main__":
    app.run_server(debug=True)
