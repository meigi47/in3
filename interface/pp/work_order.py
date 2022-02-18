#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
from utils.mapper import Mapper as factor_mapper
import os
from utils.mapper import Mapper


class Work_order(Abstract_production_obj):
   def __init__(self) -> None:
      self.data = {}
      self.module = "pp"
      self.operation = "work_order"

   def release(self, data: dict,unique_instruction="release"):
      tmp = global_data.join_url_type(
         data, self.module, self.operation, unique_instruction)
      Logger.info("这是传入req mgr的数据")
      Logger.info(tmp)
      if isinstance(tmp["case_data"],list):     #传参为list: [] 
         tmp['body'] = tmp['case_data']   
         return tmp
      mappers = Mapper.read_mapper_from_file(
         tmp.get("component"), tmp.get("path"), tmp.get("method"))
      tmp = self.replace_path(tmp)#只可在此处做关于case_data中有在path数据的替换修改，若在之前调用，无法获得mappers
      Mapper.update_case_data(mappers, tmp)
      Logger.info("这是map之后的数据")
      Logger.info(tmp)
      del tmp["body"]
      tmp["body"]=[]
      return request_manager.do_request_withdata(tmp)
      
   def finish_process(self, data: dict,unique_instruction="finish_process"):
      tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
      return request_manager.do_request(tmp)
      
   def finish_update(self, data: dict,unique_instruction="finish_update"):
      tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
      return request_manager.do_request(tmp)

   def retrieve_bomm_tree(self, data: dict,unique_instruction="retrieve_bomm_tree"):
      tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
      return request_manager.do_request(tmp)

   def get_template_of_createWO(self,path,unique_instruction="get_template_of_createWO"):
      #判断当前是否存在该文件，若有则删除
      if os.path.exists(path)==True:
         os.remove(path)
      tmp = global_data.join_url_type({},
            self.module, self.operation, unique_instruction)
      r=request_manager.do_request(tmp)
      #下载并将模板文件放在指定目录
      with open(path, 'wb') as f:
            f.write(r.content)
      f.close()

   def get_template_of_updateBOM(self,path,unique_instruction="get_template_of_updateBOM"):
      #判断当前是否存在该文件，若有则删除
      if os.path.exists(path)==True:
         os.remove(path)
      tmp = global_data.join_url_type({},
            self.module, self.operation, unique_instruction)
      r=request_manager.do_request(tmp)
      #下载并将模板文件放在指定目录
      with open(path, 'wb') as f:
            f.write(r.content)
      f.close()


   def mo_bom(self, data: dict,unique_instruction="mo_bom"):
      tmp = global_data.join_url_type(
         data, self.module, self.operation, unique_instruction)
      self.check_path_id(data,tmp)
      return request_manager.do_request(tmp)

   def get_detail_bulk_by_id(self, data: dict,unique_instruction="get_detail_bulk_by_id"):
      tmp = global_data.join_url_type(
         data, self.module, self.operation, unique_instruction)
      return request_manager.do_request(tmp)

   def save_progress(self, data: dict,unique_instruction="save_progress"):
      tmp = global_data.join_url_type(
         data, self.module, self.operation, unique_instruction)
      return request_manager.do_request(tmp)

   def finish_check(self, data: dict,unique_instruction="finish_check"):
      tmp = global_data.join_url_type(
         data, self.module, self.operation, unique_instruction)
      return request_manager.do_request(tmp)

work_order = Work_order()
