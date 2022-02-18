#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj

class Material_doc(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "wm"
        self.operation = "material_doc"

    def retrieve_material_doc_detail(self, data: dict,unique_instruction="retrieve_material_doc_detail") -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)
    
    def retrieve_tos(self, data: dict,unique_instruction="retrieve_tos") -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

    def get_tos_detal(self, data: dict,unique_instruction="get_tos_detal") -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

material_doc = Material_doc()