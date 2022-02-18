#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
import json
class Code_def(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "cofa"
        self.operation = "code_def"

    def init_global_data_codedef(self):
        code_def_config=  {
            "SD_SO_TYPE":"销售订单类型",
            "SD_SO_STATUS":"销售订单状态",
            "SPM_PO_TYPE":"采购类型",
            "IM_STOCK_TYPE":"库存类型"
        }
        for i in code_def_config:
            repos = self.retrieve({"type":i},"retrieve_tenent_code_defs")
            assert repos.status_code==200
            # 实际存放的code_def数据
            global_data.code_def.update(json.loads(repos.text))
            # code_def的索引名，供index匹配用
            global_code_def_index = global_data.data["code_def_index"]
            index_name = code_def_config[i]
            global_code_def_index[index_name] = {
                'code_def_key':(i),
                'in_key':'name',
                'out_key':'code'
            }

code_def=Code_def()