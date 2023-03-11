import dash

import os
import sys

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True

from spcashflow.database import db_mgmt

db_mgr = db_mgmt.SPCFdb_mgmt()

from spcashflow.AssetModeling import Asset, AssetRamper
from spcashflow.StructureModeling import Warehouse
from spcashflow.Utils import SPCFUtils
