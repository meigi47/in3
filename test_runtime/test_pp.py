#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#case & runtime

import pytest
from test_runtime import Test_runtime_base
from utils.global_data import global_data
from interface.uaas.uaas import account
from manager.request_manager import request_manager
from utils.logger import Logger
from utils.handler.param_to_method_handler import param_to_method_handler
# from conftest import item_gen

from utils.cases_parser import cases
from case_data.pp import manager as pp_mgr

class Test_pp(Test_runtime_base): pass
# param_to_method_handler.data["start_timestamp"]="1629202650"  #因为load data  所以这句话放在setup里面是没用的，这句话可以便于使用历史数据调试而无需改动excel文档

data=cases.get_scaled_case_data('计划管理')

'''
casepath_no0_order1_needskip
no:同用例下的excel数据实例编号
order：测试集内顺序,同测试集下的顺序编号,有这个编号的用例会在collect完毕之后进行顺序调整，使用简单的遍历插入法
needskip:用例跳过标记
'''

for i in data:

    item_name=f"test_{i['full_case_path'].replace('/','_')}_no{i['no']}_order{i['测试集内顺序'] if i['测试集内顺序'] else ''}"
    
    if '审批'  in i['full_case_path']: item_name+='_needskip' #skip功能

    setattr(Test_pp,item_name,pp_mgr.govern(i.get('full_case_path'),i.get('no')))#不知道为啥，用用例默认的path左斜杠会导致在setup class之前执行用例代码
    

    #这样修改之后，用例能否被正确调取，就取决于  
    # 1、实现中的用例路径是否正确，如果不正确会导致成为同名测试、在实例化时出现问题；
    # 2、excel中的用例路径是否存在，因为会按照excel中存在的用例路径去声明测试item