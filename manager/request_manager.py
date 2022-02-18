import utils.commons as commons
from utils.dict_obj import Dict_obj
from utils.logger import Logger
from utils.mapper import Mapper as factor_mapper
from utils.commons import *

from manager.api_manager import api_manager


class Request_manager:  # 包装request的其他因素如header
    def __init__(self) -> None:
        self.fixed_header = Dict_obj()
        self.api = api_manager
        
        # self.mapper=factor_mapper()

    # 处理header  mapped_data{'header':header,'params':params,'path':path,'body':body,'method':'get','component':'uaas','case_data':{}}
    def __decorat_request(self, mapped_data) -> dict:
        mapped_data['header'] = commons.dict_add(
            self.fixed_header.get(), mapped_data['header'])
        return mapped_data

    # data{'header':header,'params':{},'path':path,'body':{},'method':'get','component':'sd','case_data':data}
    def do_request(self, data):
        Logger.info("这是传入req mgr的数据")
        Logger.info(data)
        mapped_data = factor_mapper.map(data)
        Logger.info("这是map之后的数据")
        Logger.info(mapped_data)
        self.result = self.api.do_request(
            self.__decorat_request(mapped_data))  # 这里的返回先用原始返回吧
        return self.result

    def return_auth(self):
        return self.fixed_header.get()
    def return_api(self,data):
        return self.api.join_api_path(data)

    def do_request_withdata(self,mapped_data):#该方法仅用在case_data中存在path里的字段的数据的情况下，与上面的do_request大体一致，只是需要先对数据进行处理
        self.result = self.api.do_request(
            self.__decorat_request(mapped_data))  # 这里的返回先用原始返回吧
        return self.result

request_manager = Request_manager()
