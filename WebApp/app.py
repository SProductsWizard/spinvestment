import dash

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True

from database import db_mgmt
from AssetModeling import Asset
from AssetModeling import AssetRamper
from Utils import SPCFUtils

db_mgr = db_mgmt.SPCFdb_mgmt()
