from typing import *
from utils.logger import Logger
from copy import deepcopy as dcp
import pytest

class Abstrct_case_mgr:

    def __init__(self) -> None:
        objs=dir(self)
        self.test_instances=[]
        for i in objs:
            if i.startswith('__') or i == 'govern':
                continue 
            # print(i)
            setattr(self,i+'_instance',getattr(self,i)())
            self.test_instances.append(i+'_instance')

    def govern(self,case_path:str,no:int):
        case_found=False
        for i in self.test_instances:
            base_item=getattr(self,i)
            if case_path == base_item.full_case_path:
                tmp_item=dcp(base_item)
                tmp_item.case_instance_no=no #TODO 先转移到run batch中去做试试
                # tmp_item.load_case_data(no) #TODO 先转移到run batch中去做试试
                
                return tmp_item.run_batch
        if not case_found:Logger.warning(f'excel引用了{__name__}中未实现的用例路径 {case_path} , 用例标号 {str(no)}')
