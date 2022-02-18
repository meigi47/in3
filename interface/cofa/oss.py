#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
import json
class Oss(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "cofa"
        self.operation = "oss"

    def get_callback_parms(self, data: dict) -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "get_callback_parms")
        return request_manager.do_request(tmp) 

    def get_post_policy(self, data: dict) -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "get_post_policy")
        return request_manager.do_request(tmp)   

oss=Oss()