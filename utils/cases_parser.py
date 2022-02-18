#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.logger import Logger
from utils.decorators.log_decorator import fun_entry_exit, fun_timeit
from utils.config import config
from utils.excel_utils import excel_load
from utils import commons


class Cases_parser:  # 维护一个初级较为原始的用例结构，调用parser
    def __init__(self, case_file_root_path):
        # self.case_files=commons.recur_folder_for_file(case_file_root_path,'.xlsx$')#读取excel用例
        self.case_files=commons.recur_folder_for_file(case_file_root_path,'\.ya*ml')#读取yaml用例
        self.raw_data=[]
        for case_file in self.case_files:
            # self.raw_data+=excel_load.load_wk(case_file)#读取excel用例
            self.raw_data+=commons.read_yml(case_file)#读取yaml用例

        #以下为动态生成测试提供结构支持
        self.scaled_case_data=[]
        case_statistic={}
        for i in self.raw_data:
            tmp={}
            tmp['full_case_path']=commons.get_case_data_path(i)
            tmp['测试集内顺序']=i.get('测试集内顺序')
            if tmp['full_case_path'] not in  case_statistic:
                case_statistic[tmp['full_case_path']]=0
                tmp['no']=0
            else:
                tmp['no']=case_statistic[tmp['full_case_path']]+1
                case_statistic[tmp['full_case_path']]+=1
            tmp['data']=i
            self.scaled_case_data.append(tmp)
            
        
    def get_scaled_case_data(self,target_module:str=None):#target_module='销售分销'
        result=[]
        for i in self.scaled_case_data:
            if not target_module or i['full_case_path'].startswith(target_module):
                result+=[i]
        return result

    def get_case(self, target_case_path: str) -> dict:
        # find_from self.case_structure
        for case in self.raw_data:
            this_case_path = commons.get_case_data_path(case)
            if this_case_path == target_case_path:
                case['full_case_path'] = this_case_path
                return case
        return None

    # @fun_entry_exit()
    # @fun_timeit
    def get_cases(self, target_case_path: str) -> list:  # 返回多个case数据
        result = []
        for case in self.raw_data:
            this_case_path = commons.get_case_data_path(case)
            if this_case_path == target_case_path:
                case['full_case_path'] = this_case_path
                result.append(case)
        return result


cases = Cases_parser(config.case_file_path)
