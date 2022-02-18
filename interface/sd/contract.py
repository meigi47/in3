import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.logger import Logger

from interface.abstract_prod_op import  Abstract_production_obj


class Contract(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "sd"
        self.operation = "contract"

    

contract = Contract()
