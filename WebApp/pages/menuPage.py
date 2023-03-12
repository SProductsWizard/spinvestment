from dash import dcc
from dash import html
from dash import callback
from dash.dependencies import Input, Output, State
import dash

import Utils.GadgetsGroup as gadetsGroup
from Utils.StrUtils import StrUtils
from WebApp.pages import (
    singleAssetReplinePage,
    rampAssetPage,
    warehousePage,
    databaseStatusPage,
)

menuDict = {
    "Public Market Dashboard": ["ABS Overview", "Subprime Auto", "Consumer Loan"],
    "Credit Drill": ["Vintage Curves", "Remits Drill"],
    "Private Deal Maker": ["Repline Modeling", "Ramp Modeling", "Warehouse"],
    "Reserch Hub": ["Dealers Research", "Research Scratches"],
    "Street": ["Two Way Market"],
    "Database Management": ["Database Status", "Manage Database"],
}

menuTabs = gadetsGroup.TabsGroup(
    tabId="menuTabs", pageTitle="main", labelList=list(menuDict.keys()), vertical=True
)

submenuTabs = gadetsGroup.TabsGroup(
    tabId="submemuTabs", pageTitle="main", labelList=["Structured Products"]
)

layout = menuTabs.layout
subMenu = html.Div(children=html.Div(id="submenu-div"))
content = html.Div("this is to be developed", id="content-div")


@callback(
    Output("submenu-div", "children"),
    Input(menuTabs.tabId, "value"),
)
def clickMenu(tabValue):
    submenuLabels = menuDict[menuTabs.findLabelFromValue(tabValue)]
    submenuTabs.updateGadgest(submenuLabels)
    return submenuTabs.layout


@callback(
    Output("content-div", "children"),
    [State(menuTabs.tabId, "value"), Input(submenuTabs.tabId, "value")],
)
def clickSubMenu(menuValue, submenuValue):

    if submenuValue == "tab-replineModeling":
        return singleAssetReplinePage.layout
    elif submenuValue == "tab-rampModeling":
        return rampAssetPage.layout
    elif submenuValue == "tab-warehouse":
        return warehousePage.layout
    elif submenuValue == "tab-databaseStatus":
        return databaseStatusPage.layout
    else:
        return "TO BE DEVELOPED"
