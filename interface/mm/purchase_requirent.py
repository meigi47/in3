from interface.abstract_prod_op import Abstract_production_obj
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.logger import Logger
from utils.global_data import global_data


class Purchase_requirent(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "mm"
        self.operation = "purchase_requirent"
    
    def export_excel(self, data: dict,unique_instruction="export_excel"):
        tmp = global_data.join_url_type(
            {}, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)
    
    def create_and_submit(self, data: dict,unique_instruction="create_and_submit"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)
    def retrieve_on_pr_manage(self, data: dict,unique_instruction="retrieve_on_pr_manage"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

purchase_requirent = Purchase_requirent()
