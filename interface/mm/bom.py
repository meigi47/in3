from interface.abstract_prod_op import Abstract_production_obj
import utils.commons as commons
from manager.request_manager import request_manager
from utils.global_data import global_data
from utils.mapper import Mapper
from utils.logger import Logger


class Bom(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "mm"
        self.operation = "bom"

    def get_bom_material(self,data):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "get_bom_material")
        Logger.info("这是传入req mgr的数据")
        Logger.info(tmp)
        if isinstance(tmp["case_data"],list):     #传参为list: [] 
            tmp['body'] = tmp['case_data']   
            return tmp
        mappers = Mapper.read_mapper_from_file(
            tmp.get("component"), tmp.get("path"), tmp.get("method"))
        tmp = self.replace_path(tmp)#只可在此处做关于case_data中有在path数据的替换修改，若在之前调用，无法获得mappers
        Mapper.update_case_data(mappers, tmp)
        Logger.info("这是map之后的数据")
        Logger.info(tmp)
        return request_manager.do_request_withdata(tmp)

    def get_boms_info(self,data):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "get_boms_info")
        return request_manager.do_request(tmp)

    def update_boms(self,data):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "update_boms")
        return request_manager.do_request(tmp)

    def get_bom_material_new(self,data):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "get_bom_material_new")
        return request_manager.do_request(tmp)

bom = Bom()