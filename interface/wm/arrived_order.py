#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
class Arrived_order(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "wm"
        self.operation = "arrived_order"
    
    def detail_retrieve(self,data,unique_instruction="detail_retrieve"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp) 
    
arrived_order = Arrived_order()