#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
class Currency(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "mm"
        self.operation = "currency"

    def init_global_data_codedef(self):
        repos = self.retrieve({},"retrieve_tenent_available_currency")
        assert repos.status_code==200
        # 实际存放的code_def数据
        global_code_def = global_data.data["code_def"]
        global_code_def[self.module + self.operation] = str_utils.json_str_to_list(repos.text)
        # code_def的索引名，供index匹配用
        global_code_def_index = global_data.data["code_def_index"]
        index_names = ["结算币种","原币币种","本币币种"]
        for index_name in index_names:
            global_code_def_index[index_name] = {
                'code_def_key':(self.module + self.operation),
                'in_key':'currency_name',
                'out_key':'currency_no'
            }
        #global_data.codedef_index{结算币种：mmcurrency}
        #global_data.codedef{mmcurrency：[{currency_name:1,currency_no:2}]}




currency = Currency()
