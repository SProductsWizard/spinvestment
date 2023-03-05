import dash_core_components as dcc
import dash_html_components as html
from dash import dash_table
import pandas as pd

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app import app, db_mgr
from app import Asset, AssetRamper, SPCFUtils


def assetInputsGroup(pageTitle):
    return [
        html.Hr(),
        html.I("Notional"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-asset-notional-input",
            type="text",
            placeholder="10,000,000",
            value="10,000,000",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
        html.I("Term"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-asset-term-input",
            type="text",
            placeholder="36",
            value="36",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
        html.I("IntRate"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-asset-intrate-input",
            type="text",
            placeholder="20%",
            value="20%",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
        html.I("CDRVector"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-asset-cdrvector-input",
            type="text",
            placeholder="1 ramp 20 15",
            value="1 ramp 20 15",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
        html.I("CPRVector"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-asset-cprvector-input",
            type="text",
            placeholder="5 ramp 5 10",
            value="5 ramp 5 10",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
        html.I("SEVVector"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-asset-sevvector-input",
            type="text",
            placeholder="90",
            value="90",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
        html.I("DQVector"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-asset-dqvector-input",
            type="text",
            placeholder="1 ramp 6 6",
            value="1 ramp 6 6",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
        html.I("ServicingFees"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-asset-servicingfees-input",
            type="text",
            placeholder="0.75%",
            value="0.75%",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
    ]


def rampInputsGroup(pageTitle):
    return [
        html.Hr(),
        html.I("Commit Period"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-ramp-commit-period-input",
            type="text",
            placeholder="6",
            value="6",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
        html.I("Size Vector (mm)"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-ramp-size-vector-input",
            type="text",
            placeholder="20",
            value="20",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
        html.I("Px Vector"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-ramp-px-vector-input",
            type="text",
            placeholder="99",
            value="99",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
    ]


warehouseTranchesTerms = pd.DataFrame(
    data=[
        ["Senior", "70", "5.0%", "0.0%", "100mm"],
        ["Mezz", "85", "10.0%", "0.0%", "20mm"],
    ],
    columns=["Tranche", "advRate", "coupon", "undrawnFee", "facilitySize"],
)

warehouseFeesRatioTerms = pd.DataFrame(
    data=[
        ["0.25%", "0.25%", "0.25%"],
    ],
    columns=["trustee", "verificationAgent", "backupServicer"],
)

warehouseFeesDollarTerms = pd.DataFrame(
    data=[
        ["100,000", "5,000", "5,000", "5,000"],
    ],
    columns=[
        "legalClosing",
        "trustSetup",
        "verificationAgentSetup",
        "backupServicerSetup",
    ],
)


def warehouseInputsGroup(pageTitle):
    return [
        html.Hr(),
        html.I("Facility Commit Period"),
        html.Br(),
        dcc.Input(
            id=f"{pageTitle}-warehouse-commit-period-input",
            type="text",
            placeholder="12",
            value="12",
            style={"marginRight": "10px"},
        ),
        html.Br(),
        html.Br(),
        html.I("Debt Terms"),
        dash_table.DataTable(
            id=f"{pageTitle}-warehouse-tranch-terms-input",
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": True}
                for i in warehouseTranchesTerms.columns
            ],
            data=warehouseTranchesTerms.to_dict("records"),
            editable=True,
        ),
        html.Br(),
        html.Br(),
        html.I("Fees"),
        dash_table.DataTable(
            id=f"{pageTitle}-warehouse-fee-dollar-input",
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": True}
                for i in warehouseFeesDollarTerms.columns
            ],
            data=warehouseFeesDollarTerms.to_dict("records"),
            editable=True,
        ),
        html.Br(),
        dash_table.DataTable(
            id=f"{pageTitle}-warehouse-fee-ratios-input",
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": True}
                for i in warehouseFeesRatioTerms.columns
            ],
            data=warehouseFeesRatioTerms.to_dict("records"),
            editable=True,
        ),
    ]
