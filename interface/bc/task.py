import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
import json
import requests

class Task(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "bc"
        self.operation = "task"
        
    def export_arriver_order_items(self,data,unique_instruction="export_arriver_order_items"):
        #此处swagger所有的参数似乎和实际传参不一致，选择直接传参封装请求实现
        tmp=global_data.join_url_type(data, self.module, self.operation, unique_instruction)
        url=request_manager.return_api(tmp)
        body=data
        header_data=request_manager.return_auth()
        headers=header_data
        data=json.dumps(body)
        r=requests.post(url,data = data,headers=headers)
        Logger.info(r.text)
        return r

    def export_out_in_stock(self,data,unique_instruction="export_out_in_stock"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp) 

    def export_query_material_doc(self,data,unique_instruction="export_query_material_doc"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp) 

    def export_query_bin_stock(self,data,unique_instruction="export_query_bin_stock"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

    def export_total_stock(self,data,unique_instruction="export_total_stock"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

bc_task = Task()
