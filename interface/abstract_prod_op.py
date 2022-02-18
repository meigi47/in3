import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.logger import Logger
from utils.str_utils import str_utils
import json
from jsonpath import jsonpath
from utils.global_data import global_data
from utils.mapper import Mapper


class Abstract_production_obj:
    
    def check_path_id(self,data,tmp):#检查传入数据与path中id的匹配情况,并进行路径参数的摘出，供update与view detai类型的请求使用
        target_id_name=str_utils.get_id_name_in_path(tmp.get("path"))
        if target_id_name:
            if target_id_name not in data:
                Logger.error(f'传入interface的数据未包含指定对象所需的{target_id_name}字段，传入数据如下\n{str(data)}')
                return None
            addition = {'path_param': {target_id_name: data.get(target_id_name)}}
            commons.dict_add(tmp, addition)
            del(data[target_id_name])

    def retrieve(self, data: dict,unique_instruction="retrieve") -> dict:  # data {客户名称: 樱电电气,客户编号: KH000095}
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        if(str(tmp['method']).upper() == 'POST'):
            tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

    # data {统一信用代码: AUTO_111,客户简称: AUTO_沪电,客户名称: AUTO_沪上电气,结算币种: 156}
    def create(self, data: dict,unique_instruction="create") -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
            # Zhipeng Test,发现打印单据这个测试用例，用的是create接口，也会有传参拼接url的情况
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

    # 编辑data {account_id:893121,客户名称: AUTO_沪上电气,行业类型: AUTO_电气行业 ,联系人: AUTO_张思会}
    def update(self, data: dict,unique_instruction="update"):
        tmp = global_data.join_url_type(
            data, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)  

    def get_detail(self, data: dict,unique_instruction="get_detail"):  # 编辑data {account_id:893121}
        tmp = global_data.join_url_type(
            {}, self.module, self.operation, unique_instruction)
        self.check_path_id(data,tmp)
        tmp = commons.req_content_gen(tmp)
        return request_manager.do_request(tmp)

    def get_field_by_name(self,data:dict, filed_name:str,get_all:bool=False,uniq_instruction:str='retrieve'):#data{客户名称:wwww}   #取默认第一个或者全部
        r = self.retrieve(data,unique_instruction=uniq_instruction)
        assert (r.status_code == 200)
        r1=jsonpath(json.loads(r.text),f"$.content[*].{filed_name}")
        if not get_all:
            filed = r1[0]
        else:
            filed=r1
        return filed

    def replace_path(self,data:dict):#该方法将已初步包装的请求数据，检查case_data里是否有path里应替换的值，若存在，则替换
        mappers = Mapper.read_mapper_from_file(
            data.get("component"), data.get("path"), data.get("method"))
        case_data = data["case_data"]
        case_name_list = list(case_data.keys())
        for case_name in case_name_list:
            api_data = Mapper.get_by_alias(mappers, case_name)
            if api_data:
                api_name = name_convert_to_snake(api_data["name"])
                where = api_data["in"]
                if where == 'path':
                    old="{"+api_name+"}"
                    old_path=data['path']
                    new_path=old_path.replace(old,case_data[case_name])
                    data['path']=new_path
                    del data["case_data"][case_name]
        return data
