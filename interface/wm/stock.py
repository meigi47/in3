#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj

class Stock(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "wm"
        self.operation = "stock"
   
    def retrieve_bin_stock_list(self, data: dict,unique_instruction="retrieve_bin_stock_list") -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)
    
    def retrieve_storage_locations(self, data: dict,unique_instruction="retrieve_storage_locations") -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)
        
stock = Stock()