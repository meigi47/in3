from manager.request_manager import request_manager
from utils import commons
from interface.abstract_prod_op import Abstract_production_obj

from utils.global_data import global_data

class Goods_movement(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "wm"
        self.operation = "goods_movement"

    def get_plant_info(self, data: dict,unique_instruction="get_plant_info"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

    def picking(self, data: dict,unique_instruction="picking"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)
        
goods_movement = Goods_movement()