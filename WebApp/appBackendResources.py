from DatabaseManagement import db_mgmt

from SPCashflowModeling.AssetModeling import Asset, AssetRamper
from SPCashflowModeling.StructureModeling import Warehouse
from Utils import SPCFUtils, FigureFactory
from Markets.SPNIMonitor import ABSNIMonitor

db_mgr = db_mgmt.SPCFdb_mgmt()
absniEngine = ABSNIMonitor()
figFactoryEngine = FigureFactory.FiguerFactory(backendHandle=absniEngine)
figFactoryEngine.createFigures()
