#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#case & runtime


import pytest
from case_data import mm
from test_runtime import Test_runtime_base

'''
此类是in3 mm模块的自动化测试类
其中创建/修改采购申请和采购订单,需要依赖主数据物料,以及默认供应商和价格记录
@Attention
需要在测试之前确保相应环境中有这样的三条物料:
1.物料名称:AUTO_mm1
2.物料名称:AUTO_mm_with_supplier(默认功能供应商:AUTO_mm)
3.物料名称:AUTO_mm_with_price_record(维护了价格记录)
确保相应环境中有一条供应商:供应商名称:AUTO_mm
'''


from utils.cases_parser import cases
from case_data.mm import manager as mm_mgr
class Test_mm(Test_runtime_base): pass
# param_to_method_handler.data["start_timestamp"]="1629202650"  #因为load data  所以这句话放在setup里面是没用的，这句话可以便于使用历史数据调试而无需改动excel文档
data=cases.get_scaled_case_data('采购管理')



'''
item_name:  casepath_no0_order1_needskip
no:  同用例下的excel数据实例编号
order：  测试集内顺序,同测试集下的顺序编号,有这个编号的用例会在collect完毕之后进行顺序调整，使用简单的遍历插入法
needskip:  用例跳过标记
'''
for i in data:
    item_name=f"test_{i['full_case_path'].replace('/','_')}_no{i['no']}_order{i['测试集内顺序'] if i['测试集内顺序'] else ''}"
    if '审批'  in i['full_case_path']: item_name+='_needskip' #skip功能
    if '采购管理/采购申请列表/新建采购申请单/物料没有维护供应商' in i['full_case_path']: item_name+='_needskip' #skip功能
    setattr(Test_mm,item_name,mm_mgr.govern(i.get('full_case_path'),i.get('no')))#不知道为啥，用用例默认的path左斜杠会导致在setup class之前执行用例代码
    



# class Test_mm(Test_runtime_base):
    
    
#     # create pr
#     '''
#     采购管理/采购申请列表 新建采购申请,并且点击生成采购申请,
#     此用例创建出来的pr可以给下面的 order=4,order=9,order=12,
#     order=15的用例使用
#     '''
#     @pytest.mark.run(order=1)
#     def test_create_pr_ok_on_pr_list(self):
#         mm.Test_create_pr_ok_on_pr_list('采购管理/采购申请列表/生成采购申请单').run_batch()
    
#     '''
#     采购管理/采购申请列表 新建采购申请,并且点击保存,
#     此用例创建出来的pr可以给下面的 order=5,order=6,order=7,order=8,order=10
#     ,order=11,order=13的用例使用
#     '''
#     @pytest.mark.run(order=2)
#     def test_create_pr_with_default_supplier(self):
#         mm.Create_pr_with_default_suppliers_ok('采购管理/采购申请列表/新建采购申请单/默认供应商').run_batch()
    
#     #新建采购申请单(物料没有维护供应商)
#     # @pytest.mark.run(order=3)
#     # def test_add_pr_material_no_supplier(self):
#     #     mm.Add_pr_material_no_supplier('采购管理/采购申请列表/新建采购申请单/物料没有维护供应商').run_batch()

    
#     # update pr
#     @pytest.mark.run(order=4)
#     def test_edit_pr_ok_on_prm(self):
#         mm.Edit_pr_ok_on_prm('采购管理/采购申请管理/编辑').run_batch()
    
#     @pytest.mark.run(order=5)
#     def test_edit_pr_ok_on_pr_list(self):
#          mm.Edit_pr_ok__on_pr_list('采购管理/采购申请列表/修改/编辑采购申请单').run_batch()

#     @pytest.mark.run(order=6)
#     def test_add_item_ok_on_pr_list(self):
#         mm.Add_item_ok__on_pr_list('采购管理/采购申请列表/新增/编辑采购申请单').run_batch()

#     @pytest.mark.run(order=7)
#     def test_delete_item_ok_on_pr_list(self):
#         mm.Delete_item_ok_on_pr_list('采购管理/采购申请列表/删除/编辑采购申请单').run_batch()

#     # query pr
#     # 测试采购申请列表中的采购申请查询
#     @pytest.mark.run(order=8)
#     def test_query_pr_ok_on_pr_list(self):
#         mm.Query_pr_ok_on_pr_list('采购管理/采购申请列表/查询').run_batch()

#     # 测试采购申请管理中的采购申请查询
#     @pytest.mark.run(order=9)
#     def test_query_pr_ok_on_prm(self):
#         mm.Query_pr_ok_on_prm('采购管理/采购申请管理/查询').run_batch()  

#     @pytest.mark.run(order=10)
#     def test_export_pr_list_ok_on_pr_list(self):
#         # 采购管理/采购申请列表/导出/编辑采购申请单
#         mm.Export_pr_list_ok_on_pr_list('采购管理/采购申请列表/导出/编辑采购申请单').run_batch()

#     # 采购管理/采购申请列表/新建采购申请单/默认供应商
#     @pytest.mark.run(order=11)
#     def test_print_invoice_ok_on_prl(self):
#         mm.Print_invoice_ok_on_prl('采购管理/采购申请列表/打印单据').run_batch()
    
#     @pytest.mark.run(order=12)
#     def test_print_invoice_ok_on_prm(self):
#         mm.Print_invoice_ok_on_prm('采购管理/采购申请管理/打印单据').run_batch()
#     @pytest.mark.run(order=13)
#     def test_export_pr_manage_ok_on_pr_list(self):
#         # 采购管理/采购申请管理/导出/编辑采购申请单
#         mm.Export_pr_manage_ok_on_pr_list('采购管理/采购申请管理/导出/编辑采购申请单').run_batch()

    
#     # create po
#     '''
#     TODO 之前的用例只生成了一条可以转换为PO的PR单子,目前此用例没有可以转换的PR
#     TEMP 解决办法是order=1的那一条用例生成两条PR
#     '''
#     @pytest.mark.run(order=14)
#     def test_pr_invert_po_ok_supplier_not_null(self):
#         mm.Pr_invert_po_ok_supplier_not_null('采购管理/采购申请管理/批量转换').run_batch()

#     '''
#     用order=1那条案例生成的PR来创建PO
#     '''    
#     @pytest.mark.run(order=15)
#     def test_create_po_select_pr_ok(self):
#         mm.Create_po_with_pr_ok('采购管理/采购订单管理/手动创建PO/选择PR').run_batch()

#     # 采购管理/采购订单管理/手动创建PO/不选PR
#     '''
#     创建PO,可以给下面order=18,order=19,order=22的案例使用
#     '''
#     @pytest.mark.run(order=16)
#     def test_create_po_without_pr_ok(self):
#         mm.Create_po_without_pr_ok('采购管理/采购订单管理/手动创建PO/不选PR').run_batch()

#     '''
#     创建PO,可以给下面的order=20,order=21的案例使用
#     '''
#     @pytest.mark.run(order=17)
#     def test_create_po_with_price_ok(self):
#         mm.Create_po_with_price_ok('采购管理/采购订单管理/手动创建PO/带出价格纪录').run_batch()

#     #新建采购订单(物料维护了供应商、价格和记录)
#     @pytest.mark.run(order=18)
#     def test_add_po_item_material_has_supplierAndPrice(self):
#         mm.Add_po_item_material_has_supplierAndPrice('采购管理/采购订单管理/新建采购订单/物料维护了供应商和价格').run_batch()

       
#     # update po
#     @pytest.mark.run(order=19)
#     def test_edit_po_mm_ok(self):
#         mm.Edit_po_update('采购管理/采购订单管理/编辑PO').run_batch()

#     # 测试采购订单 物料行新增
#     @pytest.mark.run(order=20)
#     def test_edit_po_add_material(self):
#         mm.Edit_po_add_material('采购管理/采购订单管理/编辑PO/新增物料行').run_batch()

#     #测试采购订单 删除PR行
#     @pytest.mark.run(order=21)
#     def test_edit_po_delete_pr(self):
#         mm.Edit_po_delete_pr('采购管理/采购订单管理/编辑PO/删除PR行').run_batch()


#     #query po
#     @pytest.mark.run(order=22)
#     def test_query_mm_ok(self):
#         mm.case10('采购管理/采购订单管理/查询').run_batch()

    


