from interface.abstract_prod_op import Abstract_production_obj
import utils.commons as commons
from manager.request_manager import request_manager
class Material(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "mm"
        self.operation = "material"

material = Material()