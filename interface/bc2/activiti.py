import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.logger import Logger

from interface.abstract_prod_op import  Abstract_production_obj
import json
import requests
from utils.global_data import global_data

class Activiti(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "bc2"
        self.operation = "activiti"

    def get_config(self, data: dict,unique_instruction="config"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

    '''
    def need_dept(self, data: dict,unique_instruction="need_dept"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)
    '''
    def next_task_config(self, data: dict,unique_instruction="next_task_config"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

    def managers(self, data: dict,unique_instruction="managers"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

    def get_detail(self, data: dict, unique_instruction="get_detail"):
        tmp=global_data.join_url_type(data, self.module, self.operation, unique_instruction)
        tmp['path_param']={"process_id":data["process_id"],"task_id":data["task_id"]}
        url=request_manager.return_api(tmp)
        url=url+"?process_id="+data["process_id"]
        body={}
        header_data=request_manager.return_auth()
        headers=header_data
        data=json.dumps(body)        
        r=requests.get(url,data = data,headers=headers)
        Logger.info(r.text)
        return r
    
    #目前处理审批不走框架支持，直接传参数过去
    def handle_approve(self,data: dict,unique_instruction="handle_approve"):
        tmp=global_data.join_url_type(data, self.module, self.operation, unique_instruction)
        tmp['path_param']={"task_id":data["task_id"]}
        url=request_manager.return_api(tmp)
        body_data=tmp["case_data"]
        del(body_data["task_id"])
        body=body_data
        header_data=request_manager.return_auth()
        headers=header_data
        data=json.dumps(body)        
        r=requests.post(url,data = data,headers=headers)
        Logger.info(r.text)
        return r
        
activiti = Activiti()
