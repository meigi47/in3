import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.logger import Logger
from utils.mapper import Mapper as factor_mapper
from interface.abstract_prod_op import  Abstract_production_obj
from manager.api_manager import api_manager
from interface.uaas.uaas import account
import requests
import json
from utils.global_data import global_data
class Sales_order(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "sd"
        self.operation = "sales_order"
    
    def retrieve(self, data: dict,unique_instruction="retrieve") -> dict:  # data {客户名称: 樱电电气,客户编号: KH000095}
        data["all"]=True
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

    # TODO 下发审批

    #目前下发审批不走框架支持，直接传参数过去
    def create_approval(self, data: dict,unique_instruction="create_approval") -> dict:
        tmp=global_data.join_url_type(data, self.module, self.operation, unique_instruction)
        tmp['path_param']={"so_id":data["so_id"]}
        url=request_manager.return_api(tmp)
        body={}
        body["task_config"]=tmp["case_data"]["task_config"]
        header_data=request_manager.return_auth()
        headers=header_data
        data=json.dumps(body)      
        r=requests.post(url,data = data,headers=headers)
        Logger.info(r.text)
        return r
        
sales_order = Sales_order()
