 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
#case & runtime
import pytest
from case_data import wm
from test_runtime import Test_runtime_base
from utils.global_data import global_data
from interface.uaas.uaas import account
from manager.request_manager import request_manager
from utils.logger import Logger


from utils.cases_parser import cases
from case_data.wm import manager as wm_mgr
class Test_wm(Test_runtime_base): pass
# param_to_method_handler.data["start_timestamp"]="1629202650"  #因为load data  所以这句话放在setup里面是没用的，这句话可以便于使用历史数据调试而无需改动excel文档
data=cases.get_scaled_case_data('仓库管理')


'''
item_name:  casepath_no0_order1_needskip
no:  同用例下的excel数据实例编号
order：  测试集内顺序,同测试集下的顺序编号,有这个编号的用例会在collect完毕之后进行顺序调整，使用简单的遍历插入法
needskip:  用例跳过标记
'''
for i in data:
    item_name=f"test_{i['full_case_path'].replace('/','_')}_no{i['no']}_order{i['测试集内顺序'] if i['测试集内顺序'] else ''}"
    # if '审批'  in i['full_case_path']: item_name+='_needskip' #skip功能
    # if '出入库明细查询/导出'  in i['full_case_path']: item_name+='_needskip' #skip功能
    # if '导出'  not in i['full_case_path']: item_name+='_needskip' #skip功能

    setattr(Test_wm,item_name,wm_mgr.govern(i.get('full_case_path'),i.get('no')))#不知道为啥，用用例默认的path左斜杠会导致在setup class之前执行用例代码
    


# class Test_wm(Test_runtime_base):#TODO 收尾之前排序与动态class调整
    
#     def test_create_ao_ok(self):
#         wm.create_ao_ok('仓库管理/到货单/新建').run_batch() 
    
#     def test_warehousing_ref_ao(self):
#         wm.warehousing_ref_ao('仓库管理/到货单/入库').run_batch() 

#     def test_warehousing_ref_po(self):
#         wm.warehousing_ref_po('仓库管理/采购入库/采购订单').run_batch() 

#     def test_warehousing_ref_so(self):
#         wm.warehousing_ref_so('仓库管理/销售出库/参考销售订单出库').run_batch() 

#     def test_warehousing_ref_saso(self):
#         wm.warehousing_ref_saso('仓库管理/销售出库/参考销售发运单出库').run_batch() 

#     def test_get_ao_detail_ok(self):
#         wm.get_ao_detail_ok('仓库管理/到货单/详情').run_batch() 

#     @pytest.mark.run(order=1)
#     def test_submit_gain_warehousing_with_so_ok(self):
#         wm.Submit_gain_warehousing_with_so_ok('仓库管理/其他入库/701-盘盈入库').run_batch()

#     # 仓库管理/其他入库/901-调拨入库
#     @pytest.mark.run(order=10)
#     def test_submit_transfer_2_warehouse_without_so_ok(self):
#         wm.Submit_transfer_2_warehouse_without_so_ok('仓库管理/其他入库/901-调拨入库').run_batch()

#     # 仓库管理/物料凭证明细查询/物料凭证明细查询
#     @pytest.mark.run(order=12)
#     def test_query_material_doc_detail_ok(self):
#         wm.Query_material_doc_detail('仓库管理/物料凭证明细查询/物料凭证明细查询').run_batch()
    
#     @pytest.mark.run(order=13)
#     def test_query_warehousing_document_ok(self):
#         wm.Query_warehousing_document('仓库管理/出入库单据查询/出入库单据查询').run_batch()

#     @pytest.mark.run(order=14)
#     def test_submit_warehousing_with_return_so_ok(self):
#         wm.Submit_warehousing_with_return_so_ok('仓库管理/其他入库/233-退货销售订单入库').run_batch()

#     @pytest.mark.run(order=15)
#     def test_submit_warehousing_with_excep_return_af_finish(self):
#         wm.Submit_warehousing_with_excep_return_af_finish('仓库管理/其他入库/276-完工后异常退料入库').run_batch()

#     # 仓库管理/库存转储/库存转储
#     @pytest.mark.run(order=30)
#     def test_transfer_stock_ok(self):
#         wm.Transfer_stock('仓库管理/库存转储/库存转储').run_batch()

#     @pytest.mark.run(order=16)
#     def test_oos_without_mo_ok(self):
#         wm.Oos_without_mo_ok('仓库管理/其他出库/532-无工单入库-退货').run_batch()
    
#     @pytest.mark.run(order=17)
#     def test_submit_pl_oos_ok(self):
#         wm.Submit_pl_oos_ok('仓库管理/其他出库/702-盘亏出库').run_batch()

#     @pytest.mark.run(order=18)
#     def test_submit_transfer_oos_ok(self):
#         wm.Submit_transfer_oos_ok('仓库管理/其他出库/902-调拨出库').run_batch()

#     @pytest.mark.run(order=19)
#     def test_oos_by_return_po_ok(self):
#         wm.Oos_by_return_po_ok('仓库管理/其他出库/121-退货订单-退货').run_batch()

#     @pytest.mark.run(order=20)
#     def test_warehousing_by_return_po_ok(self):
#         wm.Warehousing_by_return_po_ok('仓库管理/其他入库/122-退货订单-入库').run_batch()

#     @pytest.mark.run(order=21)
#     def test_submit_oos_with_return_so_ok(self):
#         wm.Submit_oos_with_return_so_ok('仓库管理/其他出库/234-退货销售订单退回').run_batch()
    
#     @pytest.mark.run(order=22)
#     def test_create_pick_list_by_none_ok(self):
#         wm.Create_pick_list_by_none_ok('仓库管理/其他领料单/新建领料单/不关联SO').run_batch()
    
#     @pytest.mark.run(order=23)
#     def test_picking_ok(self):
#         wm.Picking_ok('仓库管理/其他领料单/领料').run_batch()
    
#     @pytest.mark.run(order=24)
#     def test_create_pick_list_ref_so(self):
#         wm.Create_pick_list_ref_so('仓库管理/其他领料单/新建领料单/关联SO').run_batch()
        
#     @pytest.mark.run(order=25)
#     def test_create_rmo_by_none_ok(self):
#         wm.Create_rmo_by_none_ok('仓库管理/其他领料单/新建退料单/不关联SO').run_batch()

#     @pytest.mark.run(order=26)
#     def test_return_material_ok(self):
#         wm.Return_material_ok('仓库管理/其他领料单/退料').run_batch()

#     @pytest.mark.run(order=27)
#     def test_create_rmo_ref_so_ok(self):
#         wm.Create_rmo_ref_so_ok('仓库管理/其他领料单/新建退料单/关联SO').run_batch()

#     @pytest.mark.run(order=2)
#     def test_other_store_return_material(self):
#         wm.other_store_return_material('仓库管理/其他入库/711-还料').run_batch()

#     @pytest.mark.run(order=3)
#     def test_bin_query(self):
#         wm.bin_query('仓库管理/库位库存查询/明细查询').run_batch()

#     def test_query_total_stock(self):
#         wm.query_total_stock('仓库管理/库位库存查询/汇总查询').run_batch()
        

#     def test_query_material_doc(self):
#         wm.query_material_doc("仓库管理/物料凭证单据查询/查询").run_batch()


#     def test_sale_out_stock_return_goods(self):
#         wm.Sale_out_stock_return_goods("仓库管理/其他入库/232-销售出库-退库").run_batch()

#     def test_work_finish_exception_into_stock(self):
#         wm.Work_finish_exception_into_stock("仓库管理/其他入库/276-完工后异常退料入库(不关联SO)").run_batch()

#     def test_initial_into_stock(self):
#         wm.Initial_into_stock("仓库管理/其他入库/561-期初初始入库").run_batch()

#     def test_production_stock_return_goods(self):
#         wm.Production_stock_return_goods("仓库管理/其他出库/132-生产入库-退货").run_batch()
    
#     def test_sale_after_out_warehouse(self):
#         wm.Sale_after_out_warehouse("仓库管理/其他出库/203-售后出库").run_batch()

#     def test_oos_af_sales_without_so(self):
#         wm.Oos_af_sales_without_so("仓库管理/其他出库/203-售后出库/不关联SO").run_batch()
    
#     def test_warehousing_ref_ck_order(self):
#         wm.Warehousing_ref_ck_order('仓库管理/其他入库/204-售后出库退回').run_batch()

#     def test_warehousing_ref_outsourcing_po(self):
#         # 仓库管理/其他入库/541-委外订单入库
#         wm.Warehousing_ref_outsourcing_po('仓库管理/其他入库/541-委外订单入库').run_batch()


#     def test_giveaway_into_stock_return_goods(self):
#         wm.Giveaway_into_stock_return_goods("仓库管理/其他出库/512-赠品入库退货").run_batch()

#     def test_entrust_external_order_out_warehouse(self):
#         wm.Entrust_external_order_out_warehouse("仓库管理/其他出库/542-委外订单出库").run_batch()

#     def test_out_stock_by_sale_transport(self):
#         wm.Out_stock_by_sale_transport("仓库管理/其他出库/601-销售发运出库").run_batch()

#     def test_out_stock_initial_return_goods(self):
#         wm.Out_stock_initial_return_goods("仓库管理/其他出库/812-期初初始退货").run_batch()

#     def test_stock_material_move(self):
#         wm.Stock_material_move("仓库管理/库存转储/库存转移").run_batch()

#     # def test_other_store_out_return_order(self):
#     #     wm.other_store_out_return_order("仓库管理/其他出库/退货订单/121-退货").run_batch() FIXME dumplicate cases

#     def test_out_in_stock_detail_query(self):
#         wm.out_in_stock_detail_query("仓库管理/出入库明细查询/查询").run_batch()

#     def test_other_storage_scrap_out_ok(self):
#         wm.other_storage_scrap_out_ok("仓库管理/其他入库/552-报废出库（取消)").run_batch()

#     def test_other_storage_sale_shipped_refund_ok(self):
#         wm.other_storage_sale_shipped_refund_ok("仓库管理/其他入库/602-销售发运退库").run_batch()
        
#     def test_export_arrivalorder_ok(self):
#         wm.export_arrival_order("仓库管理/到货单/导出").run_batch()
#     @pytest.mark.run(order=31)
#     def test_create_pick_order_ok(self):
#         wm.create_pick_order("仓库管理/工单领料/新建领料单").run_batch()
#     @pytest.mark.run(order=32)
#     def test_pick_material_ok(self):
#         wm.pick_material("仓库管理/工单领料/领料").run_batch()
#     @pytest.mark.run(order=33)
#     def test_create_return_order_ok(self):
#         wm.Create_return_order_ok("仓库管理/工单退料/新建退料单").run_batch()
#     @pytest.mark.run(order=34)
#     def test_query_return_order_detail(self):
#         wm.Query_return_order_detail("仓库管理/工单退料/详情").run_batch()

#     # def test_pick_material_ok(self):
#     #     wm.pick_material("仓库管理/工单领料/领料").run_batch()
  
#     # def test_other_store_out_with_so_ok(self):
#     #     wm.other_store_out_with_so_ok("仓库管理/其他出库/264-依据SO入库（参考261）").run_batch()   #其他出库中没有找到264类型
        
#     def test_other_store_out_abnormal_picking_ok(self):
#         wm.other_store_out_abnormal_picking_ok("仓库管理/其他出库/275-完工后异常领料").run_batch()

#     def test_other_store_out_scrap_out_ok(self):
#         wm.other_store_out_scrap_out_ok("仓库管理/其他出库/551-报废出库").run_batch()

#     def test_other_store_out_borrow_material_ok(self):
#         wm.other_store_out_borrow_material_ok("仓库管理/其他出库/712-借料").run_batch()

#     def test_other_store_out_deplete_with_so_ok(self):
#         wm.other_store_out_deplete_with_so_ok("仓库管理/其他出库/261-根据SO消耗").run_batch()

#     def test_other_storage_with_so_ok(self):
#         wm.other_storage_with_so_ok("仓库管理/其他入库/264-依据SO入库（参考261）").run_batch()
#     @pytest.mark.run(order=35)
#     def test_work_order_return_material_ok(self):
#         wm.work_order_return_material_ok("仓库管理/生产领料/工单退料/退料").run_batch()

#     def test_out_in_stock_export(self):
#         wm.out_in_stock_export("仓库管理/出入库明细查询/导出").run_batch()
  
    # def test_query_material_doc_export(self):
    #     wm.Query_material_doc_export("仓库管理/物料凭证明细查询/导出").run_batch()

    # def test_query_bin_stock_export(self):
    #     wm.query_bin_stock_export("仓库管理/库位库存查询/明细导出").run_batch()
    
    # def test_query_total_stock_export(self):
    #     wm.total_stock_export("仓库管理/库位库存查询/汇总导出").run_batch()

    # def test_submit_warehousing_with_gifts(self):
    #     wm.Submit_warehousing_with_gifts("仓库管理/其他入库/511-赠品入库").run_batch()
    
