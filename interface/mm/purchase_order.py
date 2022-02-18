import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
class Purchase_order(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "mm"
        self.operation = "purchase_order"
    
    def purchase_requirent_retrieve(self, data: dict,unique_instruction="purchase_requirent_retrieve") -> dict: 
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

    def batch_create_selected(self, data: dict) -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "batch_create_selected")
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

    def create_and_submit(self, data: dict,unique_instruction="create_and_submit") -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
            # Zhipeng Test,发现打印单据这个测试用例，用的是create接口，也会有传参拼接url的情况
        # self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

purchase_order = Purchase_order()
