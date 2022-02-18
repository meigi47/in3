import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
class Produce_manage(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "pe"
        self.operation = "produce_manage"
    
    def get_area(self, data: dict,unique_instruction="get_area"):
         tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
         return request_manager.do_request(tmp)

    def get_route(self, data: dict,unique_instruction="get_route"):
         tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
         return request_manager.do_request(tmp)

produce_manage = Produce_manage()