
from typing import *

import pytest
from requests import NullHandler
from utils.mapper import Mapper
import utils.commons as commons
from interface.sd.contract import contract
from interface.md.customer import customer
from interface.sd.sales_order import sales_order
from interface.uaas.uaas import account
from utils.logger import Logger
from interface.bc2.activiti import activiti
from manager.abstract_case import Abstract_case
import allure


from copy import deepcopy as dcp
from case_data.abstract_case_mgr import Abstrct_case_mgr


class Manager(Abstrct_case_mgr):
    def __init__(self) -> None:
        super().__init__()

    class case20(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/客户管理/正确查询', text)
        @allure.step
        def run(self):
            # @stat.mark_step#TODO 对步骤的统计修饰
            r = customer.retrieve(self.case_data['数据'][0])   
            assert (r.status_code == 200)
            #查看是否查询到的客户名称与给定的相同或包含（因为存在输入一个客户名称，会带出多个有相似名称的情况，此处按照搜查结果来判断）
            assert (len(r.json()['content']) > 0)
            check_data = self.case_data['期望校验数据'][0]
            for key,value in check_data.items():#当给出的合同编号能够搜索出多个值的时候，比较是否每个结果的合同编号都包含了期望校验数据的字符串
                for result in r.json()['content']:
                    if result.__contains__(key):
                        assert result[key].find(value) != -1
                    else:
                        Logger.error('与期望数值不符')
                        pytest.fail()

    class case25(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/客户管理/错误查询', text)
        @allure.step
        def run(self):
            # @stat.mark_step#TODO 对步骤的统计修饰
            r = customer.retrieve(self.case_data['数据'][0])   
            assert (r.status_code == 200)
            assert (len(r.json()['content']) == 0)
            #查看返回的数据中是否都包含了查询的字段
            # check_data = self.case_data['期望校验数据'][0]
            # self.compare_result_page(check_data,r)



    class case10(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/客户管理/新增客户成功', text)
        @allure.step
        def run(self):
            r = customer.create(self.case_data['数据'][0])
            check_data = self.case_data['期望校验数据'][0]
            assert (r.status_code == 200)
            assert (len(r.json()['id']) > 0)
            #查看是否新增
            customer_id=r.json()['id']
            r=customer.get_detail({'account_id':customer_id})
            check_data=self.case_data['期望校验数据'][0]    
            self.compare_result_detail(check_data,r.json())

    class case30(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/客户管理/新增客户失败', text)

        def run(self):
            r = customer.create(self.case_data['数据'][0])
            assert (r.status_code != 200)

    class case_retrieve_order_success(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/订单管理/查询正确订单', text)

        def run(self):
            r = sales_order.retrieve(self.case_data['数据'][0])
            assert (r.status_code == 200)
            assert (len(r.json()) > 0)
            check_data=self.case_data['期望校验数据'][0]
            self.compare_result_page(check_data,r)

    class case_create_order_success(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/订单管理/新增订单成功', text)

        def run(self):
            ordered_id = account.get_field_by_name(self.case_data['数据'][0],
                                                        "id")
            contract_id = contract.get_field_by_name(
                self.case_data['数据'][1], "id")
            customer_id=customer.get_field_by_name(self.case_data["数据"][2],"id")
            self.case_data["数据"][3]["orderedBy"] = ordered_id
            self.case_data["数据"][3]["contractId"] = contract_id
            self.case_data["数据"][3]["account_id"] = customer_id
            r = sales_order.create(self.case_data["数据"][3])
            assert (r.status_code == 200)
            assert (len(r.json()['new_id']) > 0)
            so_id=r.json()['new_id']
            r=sales_order.get_detail({'so_id':so_id})
            check_data=self.case_data['期望校验数据'][0]
            self.compare_result_detail(check_data,r.json())

    class case_order_detail(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/订单管理/订单信息详情', text)

        def run(self):
            so_id = sales_order.get_field_by_name(self.case_data['数据'][0], "id")
            data = {'so_id': so_id}
            r = sales_order.get_detail(data)
            assert (r.status_code == 200)
            check_data=self.case_data['期望校验数据'][0]
            self.compare_result_detail(check_data,r.json())

    class case40(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/客户管理/编辑客户信息', text)

        def run(self):
            r = customer.retrieve(self.case_data['数据'][0])
            assert (r.status_code == 200)
            assert (len(r.json()['content']) == 1)
            tmp_id = r.json()['content'][0]['id']
            tmp_no = r.json()['content'][0]['account_no']
            data = commons.dict_add(self.case_data['数据'][1], {
                'account_id': tmp_id,
                'accountNo': tmp_no
            })
            r = customer.update(data)
            assert (r.status_code == 200)
            data = {'account_id': tmp_id}
            r = customer.get_detail(data)
            assert (r.status_code == 200)
            check_data = self.case_data['期望校验数据'][0]
            self.compare_result_detail(check_data,r.json())

    class case50(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/客户管理/客户信息详情', text)

        def run(self):
            r = customer.retrieve(self.case_data['数据'][0])
            assert (r.status_code == 200)
            assert (len(r.json()['content']) == 1)
            tmp_id = r.json()['content'][0]['id']
            data = {'account_id': tmp_id}
            r = customer.get_detail(data)
            assert (r.status_code == 200)
            check_data = self.case_data['期望校验数据'][0]
            self.compare_result_detail(check_data,r.json())

    class case60(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/合同管理/新增合同成功', text)

        def run(self):
            r = customer.retrieve(self.case_data['数据'][0])
            if len(r.json()['content']) == 0:
                Logger.error('所提供的客户名称无法查询出客户')
                pytest.fail()
            accountId = r.json()['content'][0]['id']
            mgr = self.case_data['数据'][1]
            mgrName = mgr['签约人名称']
            mgrData = {'姓名': mgrName}
            r = account.retrieve(mgrData)
            mgrId = r.json()['content'][0]['id']
            data = commons.dict_add(self.case_data['数据'][2], {
                '客户id': accountId,
                '签约人id': mgrId,
                "field_values":[]
            })
            r = contract.create(data)
            #查看是否添加到合同列表，且信息无误判断增添是否成功
            assert (r.status_code == 200)
            #根据获得的合同id，通过查询该合同信息，并与之比对所填入的信息是否与其一致，判断添加合同是否成功
            assert (len(r.json()['new_id']) > 0)
            check_data = self.case_data['期望校验数据'][0]
            contract_id=r.json()['new_id']
            r=contract.get_detail({'contract_id':contract_id})
            self.compare_result_detail(check_data,r.json())

    class case70(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/合同管理/正确查询合同', text)

        def run(self):
            r = contract.retrieve(self.case_data['数据'][0])
            #查看是否查询到的合同的编号与给定的相同或包含（因为存在输入一个编号，会带出多个有相似编号的情况，此处按照搜查结果来判断）
            #若搜索结果为一或多，判断是否该结果的编号值与其相同或包含
            #若搜索结果为空，查询无结果     
            assert (r.status_code == 200)
            assert (len(r.json()['content']) > 0)
            check_data = self.case_data['期望校验数据'][0]
            self.compare_result_page(check_data,r)

    class case80(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/合同管理/错误查询合同', text)

        def run(self):
            r = contract.retrieve(self.case_data['数据'][0])
            #此处因不会有返回值，因此只需比较content的长度即可
            assert (r.status_code == 200)
            assert (len(r.json()['content']) == self.case_data['期望校验数据'][0])

    class case90(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/合同管理/编辑合同编号', text)

        def run(self):
            r = contract.retrieve(self.case_data['数据'][0])
            # 当查询一个字符串,有两个合同,一个编号与其相同,一个名字与其相同,会返回两个值,此处先做精确搜索的情况
            assert(len(r.json()['content']) != 0)# 所提供的合同编号无法查询出合同!
            for result in r.json()['content']:
                if result['contract_no'] == self.case_data['数据'][0]:
                    break
            data = self.case_data['数据'][1]
            contract_id = result['id']
            data['contract_id'] = contract_id
            r = contract.update(data)
            #再次通过id查询该合同，查看是否现在的合同编号与期望数据相符
            assert (r.status_code == 200)
            check_data = self.case_data['期望校验数据'][0]
            r=contract.get_detail({'contract_id':contract_id})

    class case100(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/合同管理/合同信息详情', text)

        def run(self):
            r = contract.retrieve(self.case_data['数据'][0])
            if len(r.json()['content']) == 0:
                Logger.error('所提供的合同编号无法查询出合同')
                pytest.fail()
            for result in r.json()['content']:
                if result['contract_no'] == self.case_data['数据'][0]:
                    break
            contract_id = result['id']  
            data = {'contract_id': contract_id}
            r = contract.get_detail(data)
            #根据所给编号查看该合同，应返回包含该合同编号的合同信息，返回不为空
            assert (r.status_code == 200)
            check_data = self.case_data['期望校验数据'][0]
            self.compare_result_detail(check_data,r.json())

    class case_order_approval_create(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/订单管理/订单下发审批状态为未下发待审批', text)
        
        def run(self):
            #检测所选订单是否为未下发状态
            so_id = sales_order.get_field_by_name(self.case_data['数据'][0], "id")
            data = {'so_id': so_id}
            r = sales_order.get_detail(data)
            assert (r.status_code == 200)
            check_data=self.case_data['期望校验数据'][0]
            if r.json().__contains__("approval_status"):
                if r.json()["approval_status"] == "R":
                    pass
                else:
                    Logger.error('该订单不为未下发待审批状态')
                    pytest.fail()
            self.compare_result_detail(check_data,r.json())
            #进行下发操作

            flow_code="SO_RELEASE"
            #查询该租户的销售订单下发配置
            r=activiti.get_config({"flow_code":flow_code})
            if r.json() == None:
                Logger.error('该租户的销售订单下发无审批流')
                pytest.fail()
            #查看下级审批节点是否需要审批(utils/map_accordance/bc2未有该接口)
            #r=activiti.need_dept({"flow_code":flow_code})
            #获得下级节点审批配置详情,此处未作详细的根据具体的配置校验
            current_user_name=account.get_from_token().json()["fullname"]
            current_user_id=account.get_from_token().json()["id"]
            org_id=account.retrieve({'姓名': current_user_name,"include_profile":"ORG"}).json()['content'][0]['organizations'][0]["id"]
            r=activiti.next_task_config({"flow_code":flow_code,"org_id":org_id})
            assignee=r.json()[0]["assignee"]
            #获取主管信息:此处框架不支持直接调用
            #r=activiti.managers({"org_id":org_id})
            #if r.json()[0]["fullname"]==current_user_name:
            #    is_leader=True
            #else:
            #    is_leader=False
            
            #下发审批，因框架不支持body中多层参数嵌套，目前直接传参给接口
            is_leader=True
            data={"task_config":[{"assignees":[{"assignee":assignee,"assignee_user_ids":[current_user_id]}],"is_leader":is_leader,"approve_notice_type":[]}],"so_id":so_id}
            r=sales_order.create_approval(data)
            #检查是否完成下发操作：订单状态是否与期望数据一致
            check_data= self.case_data['期望校验数据'][1]
            r = sales_order.get_detail({'so_id': so_id})
            self.compare_result_detail(check_data,r.json())


    class case_order_approval_reject(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/订单管理/订单下发审批驳回后状态为未下发', text)

        def run(self):
            #检测所选订单是否为未下发待审批
            so_id = sales_order.get_field_by_name(self.case_data['数据'][0], "id")
            so_name=sales_order.get_field_by_name(self.case_data['数据'][0], "batch_name")
            data = {'so_id': so_id}
            r = sales_order.get_detail(data)
            assert (r.status_code == 200)
            check_data=self.case_data['期望校验数据'][0]
            self.compare_result_detail(check_data,r.json())
            #上一个用例我们所设置的审批人是当前用户，所以搜索当前用户的待审批页面，搜索销售订单下发的审批,获取该订单审批id
            flow_code="SO_RELEASE"
            current_user_name=account.get_from_token().json()["fullname"]
            current_user_id=account.get_from_token().json()["id"]
            r=activiti.retrieve({"flow_code":flow_code,"current_user_id":current_user_id,"size":5})
            if len(r.json()['content'])==0:
                Logger.error('当前租户未有审批')
                pytest.fail()
            task_id=""
            process_id=""
            for result in r.json()['content']:
                if result["status"]=="N" and result["approval_status"]=="A" and result["batch_name"]==so_name:
                    task_id=task_id+result["task_id"]
                    process_id=process_id+result["process_id"]
            assert task_id != None
            assert process_id != None
            
            #查看该审批的详情，获取审批节点信息，
            data={"task_id":task_id,"process_id":process_id}
            r=activiti.get_detail(data)
            assert r.status_code==200
            biz_type=r.json()["biz_type"]
            assignee=""
            assignee_user_id=""
            for result in r.json()["user_tasks"]:
                if result["status"]=="-1":
                    assignee=assignee+result["assignee"]
                    assignee_user_id=assignee_user_id+result["assignee_user_id"]
            #获取主管信息:此处框架不支持直接调用
            #r=activiti.managers({"org_id":org_id})
            #if r.json()[0]["fullname"]==current_user_name:
            #    is_leader=True
            #else:
            #    is_leader=False
            #拒绝该审批
            data={"task_id":task_id,"approved":False,"process_id":process_id,"remark":None,"attachments":[],"biz_type":biz_type,"task_config":{"assignees":[{"assignee":assignee,"assignee_user_ids":[assignee_user_id]}],"is_leader":True,"approve_notice_type":[],"reject_cc_users":[],"reject_cc_notice_type":[]},"approve_form":None,"process_variables":{"need_ext_approval":False}}
            r=activiti.handle_approve(data)
            #检查是否被拒绝：订单状态是否与期望校验数据一致
            check_data= self.case_data['期望校验数据'][1]
            r = sales_order.get_detail({'so_id': so_id})
            self.compare_result_detail(check_data,r.json())

    class case_order_approval_pass(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('销售分销/订单管理/订单下发审批状态为已下发', text)

        def run(self):
            #先创立审批,因为创立完会校验，此处不再校验
            so_id = sales_order.get_field_by_name(self.case_data['数据'][0], "id")
            so_name=sales_order.get_field_by_name(self.case_data['数据'][0], "batch_name")
            r = sales_order.get_detail({'so_id': so_id})
            #默认status为N
            if r.json().__contains__("approval_status"):
                if r.json()["approval_status"]=="R":
                    c=Manager.case_order_approval_create('销售分销/订单管理/订单下发审批状态为未下发待审批')
                    c.run()
            else:
                c=Manager.case_order_approval_create('销售分销/订单管理/订单下发审批状态为未下发待审批')
                c.run()
            #上一个用例我们所设置的审批人是当前用户，所以搜索当前用户的待审批页面，搜索销售订单下发的审批,获取该订单审批id
            flow_code="SO_RELEASE"
            current_user_name=account.get_from_token().json()["fullname"]
            current_user_id=account.get_from_token().json()["id"]
            r=activiti.retrieve({"flow_code":flow_code,"current_user_id":current_user_id,"size":5})
            if len(r.json()['content'])==0:
                Logger.error('当前租户未有审批')
                pytest.fail()
            task_id=""
            process_id=""
            for result in r.json()['content']:
                if result["status"]=="N" and result["approval_status"]=="A" and result["batch_name"]==so_name:
                    task_id=task_id+result["task_id"]
                    process_id=process_id+result["process_id"]
            assert task_id != None
            assert process_id != None
            #查看该审批的详情，获取审批节点信息，
            data={"task_id":task_id,"process_id":process_id}
            r=activiti.get_detail(data)
            assert r.status_code==200
            biz_type=r.json()["biz_type"]
            assignee=""
            assignee_user_id=""
            for result in r.json()["user_tasks"]:
                if result["status"]=="-1":
                    assignee_user_id=assignee_user_id+result["assignee_user_id"]
                    break
            #当前任务不是最后一个的情况
            if r.json().__contains__("next_user_task"):
                assignee=assignee+r.json()["next_user_task"]["assignee"]
            else:
                assignee=None
                assignee_user_id=None
                
            #获取主管信息:此处框架不支持直接调用
            #r=activiti.managers({"org_id":org_id})
            #if r.json()[0]["fullname"]==current_user_name:
            #    is_leader=True
            #else:
            #    is_leader=False
            #通过该审批
            data={"task_id":task_id,"approved":True,"process_id":process_id,"remark":None,"attachments":[],"biz_type":biz_type,"task_config":{"assignees":[{"assignee":assignee,"assignee_user_ids":[assignee_user_id]}],"is_leader":True,"approve_notice_type":[],"pass_cc_users":[],"pass_cc_notice_type":[]},"approve_form":None,"process_variables":{"need_ext_approval":False}}
            r=activiti.handle_approve(data)
            if assignee != None:
                self.run()
            else:
                #开始校验
                check_data= self.case_data['期望校验数据'][0]
                r = sales_order.get_detail({'so_id': so_id})
                self.compare_result_detail(check_data,r.json())

manager=Manager()
