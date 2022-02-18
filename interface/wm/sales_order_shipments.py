import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.logger import Logger
from utils.mapper import Mapper as factor_mapper
from interface.abstract_prod_op import  Abstract_production_obj
from manager.api_manager import api_manager
from interface.uaas.uaas import account
import requests
import json
class Sales_order_shipments(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "wm"
        self.operation = "sales_order_shipments"

sales_order_shipments=Sales_order_shipments()