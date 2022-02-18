from utils.config import config
import utils.commons as commons
from utils.logger import Logger
from manager.request_manager import request_manager
from interface.abstract_prod_op import  Abstract_production_obj

from utils.global_data import global_data
class Account(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "uaas"
        self.operation = "account"
        self.login_complete=False

    def login(self) -> dict:  # 不带参数的默认login,比较原始参数比较齐全
        # pass
        # path = 'https://apiv3-qa.industics.com/service/uaas/oauth/token'
        path = '/oauth/token'
        header = {}
        header['Content-Type'] = "application/x-www-form-urlencoded"
        header['Authorization'] = config.env_data['login_info']['login_token']
        params = {'username': config.env_data['login_info']['username'], 'password': config.env_data['login_info']
                  ['password'], 'grant_type': 'password', 'pswd': config.env_data['login_info']['password']}
        r = request_manager.do_request({'header': header, 'query': params, 'path': path, 'body': {
        }, 'method': 'get', 'component': 'uaas', 'case_data': {}})  # {header,body,query,method,path,component,case_data}
        if r.status_code == 200:
            request_manager.fixed_header.add({'Accept': "application/json", 'Accept-Encoding': "gzip, deflate, br", 'Accept-Language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
                                              'Cache-Control': "no-cache", 'Connection': "keep-alive", 'T-CODE': config.env_data['login_info']['tenant_name']})
            request_manager.fixed_header.add(
                {'Authorization': r.json()['token_type']+' ' + r.json()['access_token']})
            self.login_complete=True
        else:
            Logger.warning('登陆失败')
        return r

    # def retrieve(self, data) -> dict:
    #     path = '/v2/api/tenants/{tenant_id}/users/page'
    #     # {header,body,query,method,path,component,case_data}
    #     return request_manager.do_request({'header': {}, 'query': {}, 'path': path, 'body': {}, 'method': 'get', 'component': 'uaas', 'case_data': data})
    
    def get_from_token(self,unique_instruction="get_from_token"):
        tmp = global_data.join_url_type(
            {}, self.module, self.operation,unique_instruction)
        return request_manager.do_request(tmp)

account=Account()