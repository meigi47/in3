#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
import json
import requests

class Material_pick(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "wm"
        self.operation = "material_pick"
    
    def workorder_retrieve(self,data,unique_instruction="workorder_retrieve"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp) 

    def material_in_workorder_retrieve(self,data,unique_instruction="material_in_workorder_retrieve"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp) 

    def pickorder_create(self,data,unique_instruction="pickorder_create"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp) 

    def retrieve_warehouse_location(self,data,unique_instruction="retrieve_warehouse_location"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp) 

    def have_material_location(self,data,unique_instruction="have_material_location"):
        #此处无法通过框架实现查询某个仓库下有某个物料的库位查询，选择直接传参封装请求实现
        tmp=global_data.join_url_type(data, self.module, self.operation, unique_instruction)
        url=request_manager.return_api(tmp)
        body=[tmp["case_data"]["materialSoVOS"][0]]
        header_data=request_manager.return_auth()
        headers=header_data
        data=json.dumps(body)  
        url=url+"?warehouse_no="+ tmp["case_data"]["warehouse_no"] +"&stock_type="+ tmp["case_data"]["stock_type"]
        r=requests.post(url,data = data,headers=headers)
        Logger.info(r.text)
        return r
        
    def pick_material(self,data,unique_instruction="pick_material"):
        #此处无法通过框架实现查询某个仓库下有某个物料的库位查询，选择直接传参封装请求实现
        tmp=global_data.join_url_type(data, self.module, self.operation, unique_instruction)
        url=request_manager.return_api(tmp)
        url=url.split("{")[0]+data["tr_id"]
        body=data["data"]
        header_data=request_manager.return_auth()
        headers=header_data
        data=json.dumps(body)  
        r=requests.post(url,data = data,headers=headers)
        Logger.info(r.text)
        return r 

    def pick_check(self,data,unique_instruction="pick_check"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp) 
        
    def get_pick_list_detail(self,data,unique_instruction="get_pick_list_detail"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)
    
    def retrieve_pick_list(self,data,unique_instruction="retrieve_pick_list"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

    def validate_pick_list(self,data,unique_instruction="validate_pick_list"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

material_pick = Material_pick()