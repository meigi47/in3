#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
from utils.mapper import Mapper


class Mo_warehouse_application(Abstract_production_obj):
    def __init__(self) -> None:
      self.data = {}
      self.module = "wm"
      self.operation = "mo_warehouse_application"

    def bulk(self, data: dict,unique_instruction="bulk"):
      tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
      return request_manager.do_request(tmp)
    
    def abandon(self, data: dict,unique_instruction="abandon"):
      tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
      Logger.info("这是传入req mgr的数据")
      Logger.info(tmp)
      if isinstance(tmp["case_data"],list):     #传参为list: [] 
        tmp['body'] = tmp['case_data']   
        return tmp
      mappers = Mapper.read_mapper_from_file(tmp.get("component"), tmp.get("path"), tmp.get("method"))
      tmp = self.replace_path(tmp)#只可在此处做关于case_data中有在path数据的替换修改，若在之前调用，无法获得mappers
      Mapper.update_case_data(mappers, tmp)
      Logger.info("这是map之后的数据")
      Logger.info(tmp)
      return request_manager.do_request_withdata(tmp)

mo_warehouse_application=Mo_warehouse_application()