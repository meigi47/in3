import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
class Route(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "pe"
        self.operation = "route"
    
    def retrieve_routes(self, data: dict,unique_instruction="retrieve_routes"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

route=Route()
