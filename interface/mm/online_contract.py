import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.logger import Logger
from utils.global_data import global_data


class Online_contract:
    def __init__(self) -> None:
        self.data = {}
        self.module = "sd"
        self.operation = "contract"

    def retrieve(self, data: dict) -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "retrieve")
        return request_manager.do_request(tmp)

    def create(self, data: dict) -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "create")
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

    def update(self, data: dict):
        if 'id' not in data:
            # Logger.error('查看合同详情传入的数据未包含指定合同所需的id')
            return None
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "update")
        addition = {'path_param': {'contract_id': data.get('id')}}
        commons.dict_add(tmp, addition)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

    def get_detail(self, data: dict):
        if 'id' not in data:
            # Logger.error('查看合同详情传入的数据未包含指定合同所需的id')
            return None
        tmp = global_data.join_url_type(
            {}, self.module, self.operation, "detail")
        addition = {'path_param': {'contract_id': data.get('id')}}
        commons.dict_add(tmp, addition)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)


online_contract = Online_contract()
