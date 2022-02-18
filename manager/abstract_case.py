
import pytest
from utils.cases_parser import cases
from utils.global_data import global_data
from utils.logger import Logger
from utils.str_utils import str_utils
from  copy  import deepcopy as dcp
from interface.uaas.uaas import account

def convert_data(it) :  # 对数据做递归，以支持str变量替换,返回结果,但也会原地修改
        if isinstance(it, list):
            for i in range(len(it)):
                if isinstance(it[i], str):
                    it[i] = str_utils.replace_placeholder_str(it[i])
                else:
                    convert_data(it[i])
            return it
        elif isinstance(it, dict):
            for i in it:
                if isinstance(it[i], str):
                    it[i] = global_data.query_code_def({i:it[i]})
                    it[i] = str_utils.replace_placeholder_str(it[i])
                else:
                    convert_data(it[i])
            return it
        elif not it or isinstance(it, int):
            return it
        else:
            Logger.error(f'自定义变量扫描：意外的文件数据格式！{str(it)}')
            return 

class Abstract_case:
    def __init__(self, full_case_path: str, test_main_text:str=None) -> None: #不再在这个地方默认装填
        self.full_case_path = full_case_path
        self.all_case_data=cases.get_cases(full_case_path)
        self.case_data_inited=False
        self.case_instance_no=-1 #
        
    def load_case_data(self,no:int):#同名指定case data装填
        self.case_data=self.all_case_data[no]
        if not account.login_complete:account.login()
        convert_data(self.case_data)  # 对步骤、期望数据做递归，以支持变量替换
        self.case_data_inited=True


    def run_batch(self):  # 添加支持同名用例同流程处理,在test main里面执行即可
        # 关于多个平行用例的预期不一的问题，case代码里面应当使用case data里面的预期数据，这一点由用例保证，case 代码使用预期数据的方式确实是固定的
        #如果初始化直接通过govern传了case data 那么认为用例不再执行同名多步，则此时不该用run batch
        self.load_case_data(self.case_instance_no)
        Logger.info(f'>>>>>>>>>>>>>>用例 {self.full_case_path} 开始<<<<<<<<<<<<<<')
        Logger.info('这是处理之后的case data')
        Logger.info(self.case_data)
        self.run()  # run函数是必须的
        


    def compare_result_detail(self, check_data: dict,r,data_key=None):#比较查询单个信息的response和期望检测数据是否一致
        #该方法存在一个问题，没有考虑参数嵌套列表的情况
        if not data_key:#如果不指明参与对比的字段
            check_range=list(check_data.items())
        else:#如果指明了
            check_range=[]
            for i in data_key:
                check_range.append((i,check_data[i]))

        for key,value in check_range:
            if key in r:
                if isinstance(value,dict) and isinstance(r[key],dict):#当参数嵌套字典时，递归处理进行判断
                    self.compare_result_detail(value,r[key])
                else:
                    if r[key] != value:
                        Logger.error(f'比较失败,key {key}, 预期源数据 {check_data},实际 {r}')
                        pytest.fail()
            else:
                Logger.error('与期望数值不符')
                pytest.fail()
        return None

    def compare_result_page(self, check_data: dict,r):#比较查询列表的response和期望检测数据是否一致
        for key,value in check_data.items():
            for result in r.json()['content']:
                if result.__contains__(key):
                    assert result[key].find(value) != -1
                else:
                    Logger.error('与期望数值不符')
                    pytest.fail()

    def adjust_vo(source_vo:dict,prop_map:dict):#prop_map={po_no_source : ref_no_target} 便捷一层换词
        result=dcp(source_vo)
        for source_prop,target_prop in prop_map.items():
            result[target_prop]=result.pop(source_prop)
        return result

    def query_directly(self,data:list,check_data_key,check_data_value):
        #查询时，会存在即使查询条件精确但仍会返回多个的情况，比如查编号abc，会返回abc和abcd
        #设计该方法，实现准确或许查询列表中需要的数据
        if len(data)==0:
            Logger.error('未查询到需要的结果')
            pytest.fail()
        result_data={}
        for data_list in data:
            if data_list.__contains__(check_data_key):
                if data_list[check_data_key]==check_data_value:
                    result_data=data_list
                    break
        if result_data:
            return result_data
        else:
            Logger.error('未查询到需要的结果')
            pytest.fail()    


    def is_list_same(self,list1,list2):
        #判断列表是否相同
        for i in range(len(list1)):
            j=0
            while j<len(list2):
                if list1[i]==list2[j]:
                    list2.pop(j)
                    break
                else:
                    j=j+1

                
        if len(list2)==0:
            return 1
        else:
            return 0

    def response_info(self,r,info=None):
        #该方法用于给出具体的错误提示，节省排错时间
        if r.status_code==200:
            pass
        else:
            if info != None:
                Logger.error("错误步骤发生位置于"+info)
            if r.status_code == 503:
                Logger.error('错误原因：模块正在发包')
            if r.status_code == 504:
                Logger.error('错误原因：请求超时')
            if r.status_code == 400:
                Logger.error('错误原因：请求错误')
            pytest.fail()
