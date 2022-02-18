from jsonpath import jsonpath
from interface.abstract_prod_op import Abstract_production_obj
import utils.commons as commons
from manager.request_manager import request_manager
from utils.logger import Logger
from utils.global_data import global_data


class Warehouse(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "wm"
        self.operation = "warehouse"

    def refresh_warehouse_infos(self):
        r:list=self.retrieve({},unique_instruction='retrieve_warehouses').json()
        self.data['all_warehouses']=r

    def get_warehouse_infos(self,data:dict,target_property,need_refresh=False)->list:#查询分析字段,目前只接单元素的data,且不支持bool值,如果用例编辑了仓库信息，则需要刷新refresh_warehouse_infos
        '''response
        [{
            "id" : "34957f2ff2d145d49ffe8ea73a60e68d",
            "tenant_id" : "10034",
            "warehouse_no" : "010101",
            "warehouse_no_name" : "kjt的仓库",
            "forbidden_in" : false,
            "forbidden_out" : false,
            "storage_locations" : [ {
                "id" : "19c55a4948d34813b2f98fe46bcdb44c",
                "plant_id" : "91f7a0f974f011eab8d900163e08d430",
                "storage_location_no" : "010101",
                "storage_location_name" : "kjt的库存地点"
            } ]
            }
            ]
        '''
        if not data:return None
        if 'all_warehouses' not in self.data or need_refresh:
            self.refresh_warehouse_infos()
        key,value=list(data.items())[0]
        try:
            warehouse=[x for x in self.data['all_warehouses'] if x[key]==value][0]
            results=warehouse[target_property]
            Logger.info(results)
            return results
        except:
            Logger.error(f"查询仓库信息失败{str(self.data['all_warehouses'])}")
            assert False


        
    def get_warehouse_no(self, data: dict,unique_instruction="get_warehouse_no"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)
    
    def get_warehouse_bin_info(self, data: dict,unique_instruction="get_warehouse_bin_info"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)
        
    # 查询move_types   
    def retrieve_move_types(self, data: dict,unique_instruction="retrieve_move_types"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

    def move_goods(self,data: dict,unique_instruction="move_goods"): #TODO这种后续可以优化
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

    def get_all_move_types(self,unique_instruction="get_all_move_types"):
        tmp = global_data.join_url_type(
            {}, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

    def get_move_types(self,data: dict,unique_instruction="get_move_types"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        return request_manager.do_request(tmp)

warehouse = Warehouse()