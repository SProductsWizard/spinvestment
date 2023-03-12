from dash import dcc, html, dash_table
import pandas as pd
from dash.dependencies import Output, State
from Utils.StrUtils import StrUtils


class InputsGadgetsGroup:
    def __init__(self, pageTitle):
        self.pageTitle = pageTitle
        self.entries = self._setupEntries()
        self.defaultValueList = self._setDefaultValue()
        self.titleList = self._setTitle()

        self.layout = self._setupLayout()

    def _setupEntries(self):
        return []

    def _setDefaultValue(self):
        return ""

    def _setTitle(self):
        return ""

    def getState(self):
        return [State(item, "value") for item in self.entries]

    def getOutput(self):
        return [Output(item, "value") for item in self.entries]

    def _setupLayout(self):
        res = [html.Hr()]

        for entryValue, defaultValue, title in zip(
            self.entries, self.defaultValueList, self.titleList
        ):
            res = res + [
                html.I(title),
                html.Br(),
                dcc.Input(
                    id=entryValue,
                    type="text",
                    placeholder=defaultValue,
                    value=defaultValue,
                    style={"marginRight": "10px"},
                ),
                html.Br(),
                html.Br(),
            ]

        return res


class AssetInputsGadetsGroup(InputsGadgetsGroup):
    def _setupEntries(self):
        return [
            f"{self.pageTitle}-asset-notional-input",
            f"{self.pageTitle}-asset-term-input",
            f"{self.pageTitle}-asset-intrate-input",
            f"{self.pageTitle}-asset-cdrvector-input",
            f"{self.pageTitle}-asset-cprvector-input",
            f"{self.pageTitle}-asset-sevvector-input",
            f"{self.pageTitle}-asset-dqvector-input",
            f"{self.pageTitle}-asset-servicingfees-input",
        ]

    def _setDefaultValue(self):
        return [
            "10,000,000",
            "36",
            "20%",
            "1 ramp 20 15",
            "5 ramp 5 10",
            "90",
            "1 ramp 6 6",
            "0.75%",
        ]

    def _setTitle(self):
        return [
            "Notional",
            "Term",
            "IntRate",
            "CDRVector",
            "CPRVector",
            "SEVVector",
            "DQVector",
            "ServicingFees",
        ]


class RampInputsGadgetsGroup(InputsGadgetsGroup):
    def _setupEntries(self):
        return [
            f"{self.pageTitle}-ramp-commit-period-input",
            f"{self.pageTitle}-ramp-size-vector-input",
            f"{self.pageTitle}-ramp-px-vector-input",
        ]

    def _setDefaultValue(self):
        return [
            "6",
            "20",
            "99",
        ]

    def _setTitle(self):
        return ["Commit Period", "Size Vector (mm)", "Px Vector"]


warehouseTranchesTerms = pd.DataFrame(
    data=[
        ["Senior", "67", "5.5%", "0.0%", "100mm"],
        ["Mezz", "80", "10.5%", "0.0%", "20mm"],
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


class TabsGroup:
    def __init__(self, tabId, pageTitle, labelList, vertical=False):
        self.tabId = tabId
        self.pageTitle = pageTitle
        self.vertical = vertical
        self.labelList = labelList
        self._setupGadgest()

    def updateGadgest(self, labelList):
        self.labelList = labelList
        self._setupGadgest()

    def _setupGadgest(self):

        self.labelTabValueDict = self._createLabelTabValueDict()
        self.layout = self._setupLayout()

    def _setupLayout(self):
        res = [html.Hr()]
        res = res + [
            dcc.Tabs(
                id=self.tabId,
                value=self.labelTabValueDict[self.labelList[0]],
                vertical=self.vertical,
                children=[
                    dcc.Tab(label=label, value=self.labelTabValueDict[label])
                    for label in self.labelList
                ],
            )
        ]
        return res

    def convertTabvalue(self, label):
        return f"tab-{StrUtils.CamelCase(label)}"

    def _createLabelTabValueDict(self):
        res = {}
        for item in self.labelList:
            res[item] = self.convertTabvalue(item)
        return res

    def findLabelFromValue(self, value):
        return [k for k, v in self.labelTabValueDict.items() if v == value][0]

    def getState(self):
        return State(self.tabId, "value")
