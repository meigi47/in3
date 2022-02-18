from utils.global_data import global_data
from interface.uaas.uaas import account
from manager.request_manager import request_manager
from utils.logger import Logger
from utils.handler.param_to_method_handler import param_to_method_handler
class Test_runtime_base:

    @classmethod
    def setup_class():  
        # 如果没有登录就登录
        if 'Authorization' not in request_manager.fixed_header.get():
            r = account.login()
            assert (r.status_code == 200)
        if not global_data.code_def_inited:  global_data.code_def_init()

        # param_to_method_handler.data["start_timestamp"]="1629202650"  #这句话可以便于使用历史数据调试而无需改动excel文档

    def teardown_method(self):
        Logger.info('>>>>>>>>>>>>>>用例退出<<<<<<<<<<<<<<')