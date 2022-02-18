
import re
from interface.md.customer import customer
from interface.wm.goods_movement import goods_movement
from typing import *
import pytest
import utils.commons as commons
from interface.uaas.uaas import account
from utils.logger import LOG_ENABLED, Logger
from interface.wm.arrived_order import arrived_order
# from manager.abstract_case import abstract_case
from manager.abstract_case import Abstract_case
import allure
from interface.wm.warehouse import warehouse
from interface.sd.sales_order import sales_order
from interface.wm.stock import stock
from interface.wm.otherStore import otherStore
from interface.wm.Inventory import inventory
from interface.mm.purchase_order import purchase_order
from interface.wm.material_doc import  material_doc
from interface.mm.material import material
from interface.wm.out_in_stock import out_in_stock
from interface.sd.sales_order import sales_order
from interface.wm.sales_order_shipments import sales_order_shipments
from interface.pp.work_order import work_order
from interface.wm.material_return import material_return
from interface.pe.produce_manage import produce_manage
from case_data import wm
from utils.str_utils import str_utils


from jsonpath import jsonpath
from  copy  import deepcopy as dcp
from decimal import Decimal
from interface.bc.task import bc_task
from interface.tskt.task import task
import time
import datetime
#def convert_stock_num(original_num,rounding_decimal,numerator,denominator,stock2order:bool):#用于转换数据  rouning decimal取自哪个vo要看stock2order的真假
#    stock_2_order_rate=numerator/denominator
from utils.global_data import global_data

from case_data.wm_ref import *
from case_data.abstract_case_mgr import Abstrct_case_mgr
import json

class Manager(Abstrct_case_mgr):
    def __init__(self) -> None:
        super().__init__()



    class create_ao_ok(Abstract_case): 
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/到货单/新建', text)
        def run(self):
            #用例PO新建条件 → 新建po，提取po_id 
                check_move_type_exists("101","AO")
                po_id=query_related_orders("shipped po")['id']
                # po_id='95c640558feb47f9bf9d981372a1855c'
                data=self.case_data['数据'][0]

                warehouse_no_name=data['仓库名称']

            #po_id  → 获取PO详情，提取单据内容PO_VO 
                po_vo=purchase_order.get_detail({'po_id':po_id}).json()
                storage_location_id=warehouse.get_warehouse_infos({'warehouse_no_name':warehouse_no_name},target_property='storage_locations')[0]['id']
                
            #PO_VO → 按前端默认数量规则，提交创建到货单，提取到货单 arrived_order_id
                arrived_order_creat={
                    "arrived_order_items":[
                        {
                            "po_item_id":po_vo['items'][0]['id'],
                            "quantity":data['到货数量'], #  另外这里使用字符类型的数字避免被转为e科学计数，另这个数据受单据舍入位数限制
                            "storage_location_id":storage_location_id, 
                            "field_values":[ ]
                        }
                    ],
                    "po_id":po_id, 
                    "po_no":po_vo['po_no'], 
                    "storage_location_id":storage_location_id
                }
                r=arrived_order.create(data=arrived_order_creat)
                arrived_order_id=r.json()['id']
                
            # arrived_order_id→  获取到货单详情 → 校验 内容数量 & 单据状态 等
                ao_vo=arrived_order.get_detail({'arrived_order_id':arrived_order_id}).json()
                check_condition={
                    r'$.arrived_order_items[0].arrived_qty':[float(arrived_order_creat['arrived_order_items'][0]['quantity'])],#这里转为数字
                    r'$.arrived_order_items[0].material_id':[po_vo['items'][0]['material']['material_id']],
                    r"$.po_id":[po_id]
                }
                strict_check(check_condition,ao_vo)#


                global_data.data['wm']['ao_id']=arrived_order_id
                

    class get_ao_detail_ok(Abstract_case): 
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/到货单/详情', text)
        def run(self):
            check_move_type_exists("101","AO")
            r=arrived_order.get_detail({'arrived_order_id':global_data.data['wm']['ao_id']})
            assert(r.status_code==200)

    class warehousing_ref_ao(Abstract_case): 
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/到货单/入库', text)
        def run(self):
                check_move_type_exists("101","AO")
            #使用前面创建的到货单ao_id，获取详情ao_vo，以及对应的po_id,material_id
                ao_id=global_data.data['wm']['ao_id']
                data=self.case_data['数据'][0]
                # ao_id='7205bbdcc8c7426eb7296e88e0a3c3aa'

                ao_vo=arrived_order.get_detail({'arrived_order_id':ao_id}).json()
                item_vo=ao_vo['arrived_order_items'][0]
                po_id=ao_vo['po_id']
                warehouse_no_name=data['仓库名称']
                warehouse_no=warehouse.get_warehouse_infos({'warehouse_no_name':warehouse_no_name},target_property='warehouse_no')
                material_id=jsonpath(ao_vo,f"$.arrived_order_items[0].material_id")[0]

            #选取仓库AUTO_01库位
                query_bins={
                    'warehouse_no':warehouse_no,
                    'page':0,
                    'size':9999
                }
                bins=warehouse.retrieve(data=query_bins,unique_instruction='retrieve_bins').json()
                bin_no=bins['content'][0]['bin_no']
                bin_id=bins['content'][0]['bin_id']

            #拿到po现在的单据数量，以备校验
                po_vo_1=purchase_order.get_detail({"po_id":po_id}).json()
                po_item_num_1=jsonpath(po_vo_1,f'$.items[?(@.material.material_id=="{material_id}")].open_qty')[0]

            #拿到库存地点
                storage_location_of_warehouse=warehouse.get_warehouse_infos({'warehouse_no_name':warehouse_no_name},target_property='storage_locations')[0]#这里locations一层list，jsonpath一层list，所以展开两次
                storage_location_id=storage_location_of_warehouse['id']
                warehouse_id=warehouse.get_warehouse_infos({'warehouse_no_name':warehouse_no_name},target_property='id')

            #查询库位现在的物料数量，以备校验
                query_bin_stock={
                    "warehouse_id":warehouse_id,
                    'storage_bin_id':bin_id,
                    'material_id':material_id,
                    'empty_lot_name':True,
                    'stock_type':'UU'#FIXME 做进codedef
                }
                r=stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
                tmp_qty_list=jsonpath(r.json(),f'$.content[0].total_quantity')
                material_bin_qty_1= 0 if not tmp_qty_list else tmp_qty_list[0]  #批次为空的库存

            #入库数量自动计算这个事……先统一存一个 库存数量到单据数量的转换率
                stock2order_param={
                    'rounding_decimal':item_vo['order_unit_vo']['rounding_decimal'],
                    'numerator':item_vo['conversion_numerator'],
                    'denominator':item_vo['conversion_denominator'],
                    'stock2order':True
                }

            #按照用例数量入库，返回凭证material_doc_id（material document）
                new_item_vo=dcp(item_vo)
                ao_no=ao_vo['arrived_order_no']
                item_addition={
                    'bin_id':bin_id,
                    'qty':data['入库数量'],#FIXME用例   #这里传库存数量
                    'field_values':[],
                    "destination_bin_id":bin_id,
                    #"destination_bin_no":bin_no,
                    "destination_stock_type":"UU",
                    #"destination_so_no":so_no,
                    'ref_type':"AO",# item这个字段缺失会没有成本价格
                    'ref_id':ao_id,
                    'ref_no':ao_no 
                }
                so_id=po_vo_1['items'][0].get('so_id')#判断是否项目库存
                commons.dict_add(new_item_vo,item_addition,get_bin_info_4_warehouse_movement({'库位编号':bin_no,'仓库名称':warehouse_no_name}),get_special_stock_info(so_id))
                new_item_vo=Abstract_case.adjust_vo(new_item_vo,{'item_numc':'ref_item_numc','id':'ref_item_id'})#影响回写
                warehousing_param={
                    'ref_type':"AO",
                    'ref_id':ao_id,
                    'ref_no':ao_no, #非必填不填会导致参考单据前端显示挂不上，不影响后端流程
                    'warehouse_id':warehouse_id,
                    'source_warehouse_id':None,
                    'destination_warehouse_id':warehouse_id,
                    'stock_type':'UU',
                    'plant_id':get_plant_info()['plant_id'],
                    'plant_name':get_plant_info()['plant_name'],
                    "move_reason_code":"NA",#FIXME正常操作
                    'move_reason_desc':'正常操作',#FIXME正常操作
                    'storage_location_id':storage_location_id,
                    "storage_location_name":warehouse_no_name,
                    'source_storage_location_id':None,
                    'destination_storage_location_id':storage_location_id,
                    "order_mode":"RIS",#R\I\S写死在前端代码，参考、行、单选
                    #"move_type_config_id":"91f8a4bd74f011eab8d900163e08d430",# 这个好像没有用,需要就改写move_type
                    'items':[ new_item_vo ]
                }
                commons.dict_add(warehousing_param,get_move_type({'移动类型编号':'101'}),get_warehouse_info_4_warehouse_movement({'warehouse_id':warehouse_id}))#FIXME
                tmp=warehouse.create(data=warehousing_param,unique_instruction='move_goods').json()
                material_doc_id=tmp['id']
                
            #按照md_id获取详情，校验数据行
                material_doc_vo=material_doc.get_detail({'material_doc_id':material_doc_id}).json()
                check_addition={
                            '$.items[0].material_id':[material_id],
                            '$.items[0].qty':[float(item_addition['qty'])],
                            "$.material_doc.ref_type" : ["AO"],
                            "$.material_doc.ref_id" : [ao_id],
                            '$.items[0].move_type_no':['101'],
                            '$.items[0].stock_type':['UU'],
                            '$.items[0].move_reason_code':['NA'],
                            '$.items[0].storage_location_id':[storage_location_id],
                            '$.items[0].warehouse_id':[warehouse_id],
                            '$.items[0].storage_bin_id':[bin_id]
                        }
                strict_check(check_data=check_addition,source_data=material_doc_vo)
                order_num_delta=float(convert_stock_num(check_addition['$.items[0].qty'][0],**stock2order_param))

            #按照ao_id获取详情，校验数据回写
                new_ao_vo=arrived_order.get_detail({'arrived_order_id':ao_id}).json()
                item_vo_2=new_ao_vo['arrived_order_items'][0]
                assert aprox_equal(item_vo_2['quantity_completed']-item_vo['quantity_completed'] ,order_num_delta)

            #按照po_id获取详情，校验数据回写
                po_vo_2=purchase_order.get_detail({"po_id":po_id}).json()
                po_item_num_2=jsonpath(po_vo_2,f'$.items[?(@.material.material_id=="{material_id}")].open_qty')[0]
                assert aprox_equal(po_item_num_2+order_num_delta,po_item_num_1)

            #根据仓库库位no，校验物料数量追加
                r=stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
                material_bin_qty_2=jsonpath(r.json(),f'$.content[0].total_quantity')[0] 
                assert aprox_equal(material_bin_qty_2,material_bin_qty_1+check_addition['$.items[0].qty'][0])
                        
    class warehousing_ref_po(Abstract_case):  #TODO
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/采购入库/采购订单', text)
        def run(self):
            warehousing_by_other_ways_with_po(self.case_data['数据'],'SHIPPED PO')

    class warehousing_ref_so(Abstract_case):#TODO 
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/销售出库/参考销售订单出库', text)
        def run(self):
            oos_by_other_ways_with_so(self.case_data['数据'],'COMMON SASO')
            # #创建so，获得so_vo,material_id
            #     so_id='786bc51eab45416e930bee20f7280540'#FIXME SO20210827000002
            #     so_vo_1=sales_order.get_detail({'so_id':so_id}).json()
            #     so_no=so_vo_1['so_no']
            #     item_vo_1=so_vo_1['items'][0]
            #     material_id=item_vo_1['material']['material_id']

            # #选取仓库AUTO_01库位
            #     warehouse_no_name='外购件库'#FIXME AUTO_01 from 测试用例
            #     bin=warehouse.retrieve({'warehouse_no_name':warehouse_no_name},'retrieve_bins')['content'][0]
            #     bin_no,bin_id=bin['bin_no'],bin['bin_id']

            # #拿到so现在的单据数量，以备校验
            #     so_item_num_1=jsonpath(so_vo_1,f'$.items[?(@.material.material_id=="{material_id}")].open_qty')[0]

            # #拿到库存地点
            #     storage_location_of_warehouse=warehouse.get_warehouse_infos({'warehouse_no_name':warehouse_no_name},target_property='storage_locations')[0][0]#这里locations一层list，jsonpath一层list，所以展开两次
            #     storage_location_id=storage_location_of_warehouse['id']
            #     warehouse_id=warehouse.get_warehouse_infos({'warehouse_no_name':warehouse_no_name},target_property='id')[0]

            # #查询库位现在的物料数量，以备校验
            #     query_bin_stock={
            #         "warehouse_id":warehouse_id,
            #         'storage_bin_id':bin_id,
            #         'material_id':material_id,
            #         'empty_lot_name':True,
            #         'stock_type':'UU'#FIXME 做进codedef
            #     }
            #     r=stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
            #     tmp_qty_list=jsonpath(r.json(),f'$.content[0].total_quantity')
            #     material_bin_qty_1= 0 if not tmp_qty_list else tmp_qty_list[0]  #批次为空的库存

            # #入库数量自动计算准备
            #     stock2order_param={
            #         'rounding_decimal':item_vo_1['order_unit_vo']['rounding_decimal'],
            #         'numerator':item_vo_1['conversion_numerator'],
            #         'denominator':item_vo_1['conversion_denominator'],
            #         'stock2order':True
            #     }

            # #按照用例数量入库，返回凭证material_doc_id（material document）
            #     new_item_vo=dcp(item_vo_1)
            #     item_addition={
            #         'bin_id':bin_id,
            #         'qty':'0.001',#FIXME用例   #这里传库存数量 为啥这里没被转为科学计数法啊？？？？
            #         'field_values':[],
            #         "destination_bin_id":bin_id,
            #         "destination_stock_type":"UU",
            #         'ref_type':"so",# item这个字段缺失会没有成本价格
            #         'ref_id':so_id,
            #         'ref_no':so_no 
            #     }

            #     commons.dict_add(
            #         new_item_vo,item_addition,
            #         get_bin_info_4_warehouse_movement({'库位编号':bin_no,'仓库名称':warehouse_no_name}),
            #         get_special_stock_info(so_id))

            #     new_item_vo = Abstract_case.adjust_vo(new_item_vo,{'item_numc':'ref_item_numc','id':'ref_item_id'})#影响回写
            #     warehousing_param={
            #         'ref_type':"so",
            #         'ref_id':so_id,
            #         'ref_no':so_no, #非必填不填会导致参考单据前端显示挂不上，不影响后端流程
            #         'warehouse_id':warehouse_id,
            #         'source_warehouse_id':None,
            #         'destination_warehouse_id':warehouse_id,
            #         'stock_type':'UU',
            #         "move_reason_code":"NA",#FIXME正常操作
            #         'move_reason_desc':'正常操作',#FIXME正常操作
            #         'storage_location_id':storage_location_id,
            #         "storage_location_name":warehouse_no_name,#FIXME
            #         'source_storage_location_id':None,
            #         'destination_storage_location_id':storage_location_id,
            #         "order_mode":"RIS",#R\I\S写死在前端代码，参考、行、单选
            #         #"move_type_config_id":"91f8a4bd74f011eab8d900163e08d430",# 这个好像没有用,需要就改写move_type
            #         'items':[ new_item_vo ]
            #     }
            #     commons.dict_add(
            #         warehousing_param,
            #         get_move_type({'move_type_no':'101'}),
            #         get_plant_info(),
            #         get_warehouse_info_4_warehouse_movement({'warehouse_id':warehouse_id}))#FIXME
            #     tmp=warehouse.create(data=warehousing_param,unique_instruction='move_goods').json()
            #     material_doc_id=tmp['id']
            # #按照md_id获取详情，校验数据行
            #     material_doc_vo=material_doc.get_detail({'material_doc_id':material_doc_id}).json()
            #     check_addition={
            #                 '$.items[0].material_id':[material_id],
            #                 '$.items[0].qty':[float(item_addition['qty'])],#FIXME用例
            #                 "$.material_doc.ref_type" : ["so"],
            #                 "$.material_doc.ref_id" : [so_id],
            #                 '$.items[0].move_type_no':['101'],#FIXME
            #                 '$.items[0].stock_type':['UU'],
            #                 '$.items[0].move_reason_code':['NA'],
            #                 '$.items[0].storage_location_id':[storage_location_id],
            #                 '$.items[0].warehouse_id':[warehouse_id],
            #                 '$.items[0].storage_bin_id':[bin_id]
            #             }
            #     strict_check(check_data=check_addition,source_data=material_doc_vo)
            #     order_num_delta=float(convert_stock_num(check_addition['$.items[0].qty'][0],**stock2order_param))

            # #按照so_id获取详情，校验数据回写
            #     so_vo_2=sales_order.get_detail({"so_id":so_id}).json()
            #     so_item_num_2=jsonpath(so_vo_2,f'$.items[?(@.material.material_id=="{material_id}")].open_qty')[0]
            #     assert aprox_equal(so_item_num_2+order_num_delta,so_item_num_1)

            # #根据仓库库位no，校验物料数量追加
            #     r=stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
            #     material_bin_qty_2=jsonpath(r.json(),f'$.content[0].total_quantity')[0] 
            #     assert aprox_equal(material_bin_qty_2,material_bin_qty_1+check_addition['$.items[0].qty'][0])
                
    class warehousing_ref_saso(Abstract_case): #TODO
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/销售出库/参考销售发运单出库', text)
        def run(self):
            # FH20210910000067
            oos_by_other_ways_with_so(self.case_data['数据'],'SHIPPED SOSA')
            # #创建so，获得so_vo,material_id
            #     so_id='786bc51eab45416e930bee20f7280540'#FIXME SO20210827000002
            #     so_vo_1=sales_order.get_detail({'so_id':so_id}).json()
            #     so_no=so_vo_1['so_no']
            #     item_vo_1=so_vo_1['items'][0]
            #     material_id=item_vo_1['material']['material_id']
            
            # #选取仓库AUTO_01库位
            #     warehouse_no_name='外购件库'#FIXME AUTO_01 from 测试用例
            #     bin=warehouse.retrieve({'warehouse_no_name':warehouse_no_name},'retrieve_bins')['content'][0]
            #     bin_no,bin_id=bin['bin_no'],bin['bin_id']

            # #拿到so现在的单据数量，以备校验
            #     so_item_num_1=jsonpath(so_vo_1,f'$.items[?(@.material.material_id=="{material_id}")].open_qty')[0]

            # #拿到库存地点
            #     storage_location_of_warehouse=warehouse.get_warehouse_infos({'warehouse_no_name':warehouse_no_name},target_property='storage_locations')[0][0]#这里locations一层list，jsonpath一层list，所以展开两次
            #     storage_location_id=storage_location_of_warehouse['id']
            #     warehouse_id=warehouse.get_warehouse_infos({'warehouse_no_name':warehouse_no_name},target_property='id')[0]

            # #查询库位现在的物料数量，以备校验
            #     query_bin_stock={
            #         "warehouse_id":warehouse_id,
            #         'storage_bin_id':bin_id,
            #         'material_id':material_id,
            #         'empty_lot_name':True,
            #         'stock_type':'UU'#FIXME 做进codedef
            #     }
            #     r=stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
            #     tmp_qty_list=jsonpath(r.json(),f'$.content[0].total_quantity')
            #     material_bin_qty_1= 0 if not tmp_qty_list else tmp_qty_list[0]  #批次为空的库存
            # #创建saso
            #     saso_param={
            #         "so_infos":[{ 'so_id':so_id }],
            #         'so_shipment_lines':{
            #             'material_id':material_id,
            #             'so_id':so_id,
            #             'so_item_id':item_vo_1['id'],
            #             'total_qty':0.01,#FIXME
            #             'storage_location_id':storage_location_id
            #                             },
            #         'receipt_save_address':{ #FIXME 暂时这个没啥意义不用强求吧？
            #                 "id" : "223437947498976512",
            #                 "country" : '100000',
            #                 "province" : '460000',
            #                 "city" : '460100',
            #                 "address_detail" : "333",
            #                 "full_address" : "中国海南省海口市333"
            #         },
            #         "shipment_save_address": {
            #             "country": "100000",
            #             "province": "110000",
            #             "city": "110100",
            #             "district": None,
            #             "address_detail": "22",
            #             "full_address": "中国北京市北京市22"
            #                                 },
            #         "so_ids": [so_id]
            #     }
            #     saso_id=sales_order_shipments.create(saso_param).json()['id']
            #     saso_vo=sales_order_shipments.get_detail({'sales_order_shipment_id':saso_id})
            #     saso_no=saso_vo['shipment_no']
            #     saso_item_vo=saso_vo['so_shipment_lines'][0]

            # #按照用例数量入库，返回凭证material_doc_id（material document）
            #     new_item_vo=dcp(saso_item_vo)
            #     item_addition={
            #         'bin_id':bin_id,
            #         'qty':'0.001',#FIXME用例   #这里传库存数量 为啥这里没被转为科学计数法啊？？？？
            #         'field_values':[],
            #         "destination_bin_id":bin_id,
            #         "destination_stock_type":"UU",
            #         'ref_type':"saso",# item这个字段缺失会没有成本价格
            #         'ref_id':saso_id,
            #         'ref_no':saso_no 
            #     }

            #     commons.dict_add(
            #         new_item_vo,item_addition,
            #         get_bin_info_4_warehouse_movement({'库位编号':bin_no,'仓库名称':warehouse_no_name}),
            #         get_special_stock_info(so_id))

            #     new_item_vo = Abstract_case.adjust_vo(new_item_vo,{'item_numc':'ref_item_numc','id':'ref_item_id'})#影响回写
            #     warehousing_param={
            #         'ref_type':"saso",
            #         'ref_id':saso_id,
            #         'ref_no':saso_no, #非必填不填会导致参考单据前端显示挂不上，不影响后端流程
            #         'warehouse_id':warehouse_id,
            #         'source_warehouse_id':None,
            #         'destination_warehouse_id':warehouse_id,
            #         'stock_type':'UU',
            #         "move_reason_code":"NA",#FIXME正常操作
            #         'move_reason_desc':'正常操作',#FIXME正常操作
            #         'storage_location_id':storage_location_id,
            #         "storage_location_name":warehouse_no_name,#FIXME
            #         'source_storage_location_id':None,
            #         'destination_storage_location_id':storage_location_id,
            #         "order_mode":"RIS",#R\I\S写死在前端代码，参考、行、单选
            #         #"move_type_config_id":"91f8a4bd74f011eab8d900163e08d430",# 这个好像没有用,需要就改写move_type
            #         'items':[ new_item_vo ]
            #     }
            #     commons.dict_add(
            #         warehousing_param,
            #         get_move_type({'move_type_no':'231'}),
            #         get_plant_info(),
            #         get_warehouse_info_4_warehouse_movement({'warehouse_id':warehouse_id}))#FIXME
            #     tmp=warehouse.create(data=warehousing_param,unique_instruction='move_goods').json()
            #     material_doc_id=tmp['id']

            # #按照md_id获取详情，校验数据行
            #     material_doc_vo=material_doc.get_detail({'material_doc_id':material_doc_id}).json()
            #     check_addition={
            #                 '$.items[0].material_id':[material_id],
            #                 '$.items[0].qty':[float(item_addition['qty'])],#FIXME用例
            #                 "$.material_doc.ref_type" : ["saso"],
            #                 "$.material_doc.ref_id" : [so_id],
            #                 '$.items[0].move_type_no':['231'],#FIXME
            #                 '$.items[0].stock_type':['UU'],
            #                 '$.items[0].move_reason_code':['NA'],
            #                 '$.items[0].storage_location_id':[storage_location_id],
            #                 '$.items[0].warehouse_id':[warehouse_id],
            #                 '$.items[0].storage_bin_id':[bin_id]
            #             }
            #     strict_check(check_data=check_addition,source_data=material_doc_vo)
            #     order_num_delta=check_addition['$.items[0].qty'][0]

            # #按照so_id获取详情，校验数据回写
            #     so_vo_2=sales_order.get_detail({"so_id":so_id}).json()
            #     so_item_num_2=jsonpath(so_vo_2,f'$.items[?(@.material.material_id=="{material_id}")].open_qty')[0]
            #     assert aprox_equal(so_item_num_2+order_num_delta,so_item_num_1)

            # #根据仓库库位no，校验物料数量追加
            #     r=stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
            #     material_bin_qty_2=jsonpath(r.json(),f'$.content[0].total_quantity')[0] 
            #     assert aprox_equal(material_bin_qty_2,material_bin_qty_1+check_addition['$.items[0].qty'][0])

    '''
    仓库管理->其他入库->701-盘盈入库，关联一条SO，手动添加物料信息，
    点击提交按钮，期望结果为：入库成功，库存增加SO项目库存
    看起来QA环境有bug，701关联SO入库，结果入成了通用库存
    '''
    class Submit_gain_warehousing_with_so_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/701-盘盈入库', text)
        @allure.step
        def run(self):
            warehousing_by_other_ways_with_so(self.case_data["数据"])
            
    class Submit_transfer_2_warehouse_without_so_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/901-调拨入库', text)
        @allure.step
        def run(self):
            warehousing_by_other_ways_without_so(self.case_data["数据"])     
            
    class Transfer_stock(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/库存转储/库存转储', text)
        @allure.step
        def run(self):
            # 查询一笔可以转移的，自动化测试转入的项目料
            material_info = material.retrieve(self.case_data['数据'][0]).json()['content'][0]
            material_id = material_info['id']
            material_no = material_info['material_no']
            destination_bin_info = get_bin_info_4_warehouse_movement(self.case_data['数据'][1])
            destination_warehouse = get_warehouse_info_4_warehouse_movement(self.case_data['数据'][1])
            warehouse_id = destination_warehouse['destination_warehouse_id']
            storage_bin_id = destination_bin_info['destination_bin_id']
            query_bin_stock_param_b4 = {
                'material_id':material_id,
                'material_no':material_no,
                'warehouse_id':warehouse_id,
                'storage_bin_id':storage_bin_id,
                'special_stock_type':'SO'
            }
            if len(stock.retrieve_bin_stock_list(query_bin_stock_param_b4).json()) == 0 :
                Logger.info("系统没有可用的项目料！！！")
                pytest.skip()
                
            stock_info_b4 = stock.retrieve_bin_stock_list(query_bin_stock_param_b4).json()[0]
            qty_b4_move = stock_info_b4['total_quantity']
            so_id = stock_info_b4['so_id']
            so_no = stock_info_b4['so_no']
            ref_type = 'SO'
            stock_type = "Q"
            source_special_stock = True
            special_stock_type = 'SO'
            # 转储的数量
            move_qty = self.case_data['数据'][0]['数量']

            # 转储
            item = commons.dict_add({
                "source_stock_type":"UU",
                "material_id":material_id,
                "qty":move_qty,
                "source_so_id":so_id,
                "source_so_no":so_no,
                "source_special_stock":source_special_stock,
                "source_special_stock_ref_id":so_id,
                "source_special_stock_ref_type":ref_type,
                "source_special_stock_type":stock_type,
                "destination_stock_type":"UU",
                "destination_special_stock":False
            },destination_bin_info,commons.dict_key_replace_key_word(destination_bin_info,'destination','source'))
            body=commons.dict_add({
                "move_reason_code":"NA",
                "move_reason_desc":"正常操作",
                "items":[item]
            },get_plant_info(),get_move_type(self.case_data['数据'][0]),destination_warehouse,commons.dict_key_replace_key_word(destination_warehouse,'destination','source'))
            r = goods_movement.create(body)

            # 校验：调拨数量+剩余的数量=原始的数量
            query_stock_dict_af = {
                'special_stock_type':special_stock_type,
                'material_id':material_id,
                'material_no':material_no,
                'warehouse_id':destination_warehouse['destination_warehouse_id'],
                'storage_bin_id':destination_bin_info['destination_bin_id'],
                'so_id':so_id
            }
            stock_info_af = stock.retrieve_bin_stock_list(query_stock_dict_af)
            qty_af_move = stock_info_af.json()[0]['total_quantity']
            assert(r.status_code == 200)
            assert(aprox_equal(qty_af_move+float(move_qty),qty_b4_move))
            assert(len(r.json()['id']) > 0)

    class Query_material_doc_detail(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/物料凭证明细查询/物料凭证明细查询', text)
        @allure.step
        def run(self):
            r = material_doc.retrieve_material_doc_detail(get_move_type(self.case_data['数据'][0]))
            assert (len(r.json()['content']) > 0)
    class Query_warehousing_document(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/出入库单据查询/出入库单据查询', text)
        @allure.step
        def run(self):
            r = material_doc.retrieve_tos(get_move_type(self.case_data['数据'][0]))
            assert (len(r.json()['content']) > 0)

    class Submit_warehousing_with_return_so_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/233-退货销售订单入库', text)
        @allure.step
        def run(self):
            warehousing_by_other_ways_with_so(self.case_data["数据"],'RETURN SRSO')
            
    class Submit_oos_with_return_so_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/234-退货销售订单退回', text)
        @allure.step
        def run(self):
            oos_by_other_ways_with_so(self.case_data["数据"],'RETURN SRSO')

    # 276-完工后异常退料入库
    class Submit_warehousing_with_excep_return_af_finish(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/276-完工后异常退料入库', text)
        @allure.step
        def run(self):
            warehousing_by_other_ways_with_so(self.case_data["数据"],'SHIPPED SO')
            
    # 532-无工单入库-退货
    class Oos_without_mo_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/532-无工单入库-退货', text)
        @allure.step
        def run(self):
            oos_by_other_ways_with_so(self.case_data["数据"])

    class Submit_pl_oos_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/702-盘亏出库', text)
        @allure.step
        def run(self):
            oos_by_other_ways_with_so(self.case_data["数据"])

    class Submit_transfer_oos_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/902-调拨出库', text)
        @allure.step
        def run(self):
            oos_by_other_ways_with_so(self.case_data["数据"])

    class Oos_by_return_po_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/121-退货订单-退货', text)
        @allure.step
        def run(self):
            oos_by_other_ways_with_po(self.case_data["数据"])

    class Warehousing_by_return_po_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/122-退货订单-入库', text)
        @allure.step
        def run(self):
            warehousing_by_other_ways_with_po(self.case_data["数据"])

    class Create_pick_list_by_none_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他领料单/新建领料单/不关联SO', text)
        def run(self):
            new_mo = create_pick_list_by_none(self.case_data['数据'])
            # 放入global_data
            if global_data.data.__contains__('wm'):
                global_data.data['wm']['po_vo'] = new_mo[0]
            else:
                global_data.data['wm'] = {'po_vo':new_mo[0]}

    class Create_pick_list_ref_so(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他领料单/新建领料单/关联SO', text)
        def run(self):
            create_pick_list_ref_so(self.case_data['数据'])

    class Create_rmo_by_none_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他领料单/新建退料单/不关联SO', text)
        def run(self):
            new_mo = create_pick_list_by_none(self.case_data['数据'],'OPKRT')
            # 放入global_data
            if global_data.data.__contains__('wm'):
                global_data.data['wm']['rm_vo'] = new_mo[0]
            else:
                global_data.data['wm'] = {'rm_vo':new_mo[0]}
            
    
    class Create_rmo_ref_so_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他领料单/新建退料单/关联SO', text)
        def run(self):
            create_pick_list_ref_so(self.case_data['数据'],'OPKRT','RETURN SRSO')


    class Picking_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他领料单/领料', text)
        def run(self):
            # 先尝试从global_data中获取po_vo，如果没有的话则自己创建
            if global_data.data.__contains__('wm') and global_data.data['wm'].__contains__('po_vo'):
                pick = global_data.data['wm']['po_vo']
            else :
                pick = create_pick_list_by_none(wm.Manager.Create_pick_list_by_none_ok('仓库管理/其他领料单/新建领料单/不关联SO').case_data['数据'])[0]
            pick_detail =  material_pick.get_pick_list_detail({'tr_id':pick['id']}).json()
            # 需要领的数量
            req_pick_qty = pick_detail['tr_items'][0]['total_quantity']
            
            # 如果领料数量大于需要的总数，则失败
            if req_pick_qty < int(self.case_data['数据'][1]['出库数量']):
                Logger.error("出库数量过大！！！")
                pytest.fail()

            # 获取领料前的库存
            bin_info = get_bin_info_4_warehouse_movement(self.case_data['数据'][0])
            warehouse_info = get_warehouse_info_4_warehouse_movement(self.case_data['数据'][0])
            query_bin_stock = {
                "warehouse_id":warehouse_info['destination_warehouse_id'],
                'storage_bin_id':bin_info['destination_bin_id'],
                'material_id':pick_detail['tr_items'][0]['material_id'],
                'empty_lot_name':True,
                'stock_type':'UU' #FIXME 做进codedef
            }
            stock_info_b4 = stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
            tmp_qty_list=jsonpath(stock_info_b4.json(),f'$.content[0].total_quantity')
            material_bin_qty_b4 = 0 if not tmp_qty_list else tmp_qty_list[0]
            Logger.info('material_bin_qty_b4:'+str(material_bin_qty_b4))

            body =commons.dict_add(
                {
                'tr_id':pick['id'],
                "ref_no": pick['tr_no'],
                "ref_id": pick['id'],
                "ref_type": pick['delivery_order_name'],
                "move_reason_code": "NA",
                "move_reason_desc": "正常操作",
                "items": [commons.dict_add({
                    "material_id": pick_detail['tr_items'][0]['material_id'],
                    "move_type_id": pick_detail['tr_items'][0]['move_type_id'],
                    "move_type_no": pick_detail['tr_items'][0]['move_type_no'],
                    "move_type_desc": pick_detail['tr_items'][0]['move_type_desc'],
                    "ref_item_id": pick_detail['tr_items'][0]['id'],
                    "qty": self.case_data['数据'][1]['出库数量'],
                    "source_stock_type": "UU",
                    "source_special_stock": False,
                },commons.dict_key_replace_key_word(bin_info,'destination','source')
                )]
            },get_plant_info(),commons.dict_key_replace_key_word(warehouse_info,'destination','source'),get_move_type(self.case_data['数据'][1])
            )
            r = goods_movement.picking(body)
            assert(r.status_code == 200)
            # 校验1 入库成功,库存减一 FIXME in3 bug
            # stock_info_af = stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
            # material_bin_qty_af = jsonpath(stock_info_af.json(),f'$.content[0].total_quantity')[0] 
            # Logger.info('material_bin_qty_af:'+str(material_bin_qty_af))
            # assert aprox_equal(material_bin_qty_af,material_bin_qty_b4-self.case_data['数据'][1]['出库数量']) 
            # 校验2 领料单状态变化
            # 当前的pick_detail
            pick_detail =  material_pick.get_pick_list_detail({'tr_id':pick['id']}).json()
            finish_status = pick_detail['tr_items'][0]['finish_status']
            # 如果领料的数量小于开领料单的总数，则状态是部分完成，如果等于领料单的总数，则全部完成
            if req_pick_qty > int(self.case_data['数据'][1]['出库数量']):
                assert(finish_status == 1)
            elif req_pick_qty == int(self.case_data['数据'][1]['出库数量']):
                assert(finish_status == 2)



    class Return_material_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他领料单/退料', text)
        def run(self):
            # 先调用create_pick_list_by_none创建rmo
            if global_data.data.__contains__('wm') and global_data.data['wm'].__contains__('rm_vo'):
                rmo = global_data.data['wm']['rm_vo']
            else:
                rmo = create_pick_list_by_none(wm.Manager.Create_rmo_by_none_ok('仓库管理/其他领料单/新建退料单/不关联SO').case_data['数据'],'OPKRT')[0]
            rmo_detail =  material_pick.get_pick_list_detail({'tr_id':rmo['id']}).json()

            # 需要领的数量
            req_pick_qty = rmo_detail['tr_items'][0]['total_quantity']
            
            # 如果领料数量大于需要的总数，则失败
            if req_pick_qty < int(self.case_data['数据'][1]['出库数量']):
                Logger.error("出库数量过大！！！")
                pytest.fail()

            # 获取领料前的库存
            bin_info = get_bin_info_4_warehouse_movement(self.case_data['数据'][0])
            warehouse_info = get_warehouse_info_4_warehouse_movement(self.case_data['数据'][0])
            query_bin_stock = {
                "warehouse_id":warehouse_info['destination_warehouse_id'],
                'storage_bin_id':bin_info['destination_bin_id'],
                'material_id':rmo_detail['tr_items'][0]['material_id'],
                'empty_lot_name':True,
                'stock_type':'UU' #FIXME 做进codedef
            }
            stock_info_b4 = stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
            tmp_qty_list=jsonpath(stock_info_b4.json(),f'$.content[0].total_quantity')
            material_bin_qty_b4 = 0 if not tmp_qty_list else tmp_qty_list[0]
            Logger.info('material_bin_qty_b4:'+str(material_bin_qty_b4))
            body =commons.dict_add(
                {
                'tr_id':rmo['id'],
                "ref_no": rmo['tr_no'],
                "ref_id": rmo['id'],
                "ref_type": rmo['delivery_order_name'],
                "move_reason_code": "NA",
                "move_reason_desc": "正常操作",
                "items": [commons.dict_add({
                    "material_id": rmo_detail['tr_items'][0]['material_id'],
                    "move_type_id": rmo_detail['tr_items'][0]['move_type_id'],
                    "move_type_no": rmo_detail['tr_items'][0]['move_type_no'],
                    "move_type_desc": rmo_detail['tr_items'][0]['move_type_desc'],
                    "ref_item_id": rmo_detail['tr_items'][0]['id'],
                    "qty": self.case_data['数据'][1]['出库数量'],
                    "destination_stock_type": "UU",
                    "destination_special_stock": False,
                },bin_info
                )]
            },get_plant_info(),warehouse_info,get_move_type(self.case_data['数据'][1])
            )
            r = goods_movement.picking(body)
            assert(r.status_code == 200)
            # 校验1 入库成功,库存加一 FIXME in3 bug
            # stock_info_af = stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
            # material_bin_qty_af = jsonpath(stock_info_af.json(),f'$.content[0].total_quantity')[0] 
            # Logger.info('material_bin_qty_af:'+str(material_bin_qty_af))
            # assert aprox_equal(material_bin_qty_af,material_bin_qty_b4+self.case_data['数据'][1]['出库数量']) 
            
            # 校验2 领料单状态变化
            # 当前的rmo_detail
            rmo_detail =  material_pick.get_pick_list_detail({'tr_id':rmo['id']}).json()
            finish_status = rmo_detail['tr_items'][0]['finish_status']
            # 如果领料的数量小于开领料单的总数，则状态是部分完成，如果等于领料单的总数，则全部完成
            if req_pick_qty > int(self.case_data['数据'][1]['出库数量']):
                assert(finish_status == 1)
            elif req_pick_qty == int(self.case_data['数据'][1]['出库数量']):
                assert(finish_status == 2)

    

    class other_store_return_material(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/711-还料', text)

        def run(self):
            warehousing_by_other_ways_with_so(self.case_data["数据"])       #调用通用方法
    class bin_query(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/库位库存查询/明细查询', text)
        
        def run(self):
            stock_type = self.case_data['数据'][0]['库存类型']
            r = inventory.retrieve({"stock_type":stock_type})

            assert (r.status_code == 200)
            assert (len(r.json()['content']) >= self.case_data['期望校验数据'][0])

    #汇总查询库位库存
    class query_total_stock(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/库位库存查询/汇总查询', text)
        
        def run(self):
            material_list = material.retrieve({"material":self.case_data['数据'][0]['物料名称']})
            material_id = material_list.json()['content'][0]['id']              
        
            storage_location_id = None
            storage = stock.retrieve_storage_locations({"storage_location_name":self.case_data['数据'][0]['库存地点']})
            for i in range(len(storage.json()['content'])):
                item = storage.json()['content'][i]
                if(item['storage_location_name'] == self.case_data['数据'][0]['库存地点']):
                    storage_location_id = item['id']

            param = {
                'material_id':material_id,
                'storage_location_id':storage_location_id
            } 

            r = stock.retrieve(param)
            assert (r.status_code == 200)
            assert (len(r.json()['content']) >= self.case_data['期望校验数据'][0])


    #查询物料凭证单据
    class query_material_doc(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/物料凭证单据查询/查询', text)
        
        def run(self):
            #从global_data中获取之前生成的material_doc_no
            material_doc_no = global_data.data['wm']['material_doc_no']
            r = material_doc.retrieve({"doc_no":material_doc_no})
            assert (r.status_code == 200)
            assert (len(r.json()['content']) >= self.case_data['期望校验数据'][0])



    #其他入库/561-期初初始入库(关联SO)
    class Initial_into_stock(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/561-期初初始入库', text)
        def run(self):
            move_type_no = self.case_data['数据'][1]['移动类型编号']
            #若租户没有该移动类型，则跳过
            check_move_type_exists(move_type_no,'SO')
            warehousing_by_other_ways_with_so(self.case_data["数据"])


    #其他入库/276-完工后异常退料入库(不关联SO)
    class Work_finish_exception_into_stock(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/276-完工后异常退料入库(不关联SO)', text)
        def run(self):
            move_type_no = self.case_data['数据'][1]['移动类型编号']
            #若租户没有该移动类型，则跳过
            check_move_type_exists(move_type_no,'SO')
            warehousing_by_other_ways_without_so(self.case_data["数据"])


    #其他入库/132-生产入库-退货
    class Production_stock_return_goods(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/132-生产入库-退货', text)
        def run(self):
            data_list = self.case_data["数据"]

            #前置操作，生成MO-->释放-->完工-->完成工单-->生产入库
            mo = MO_finish_and_into_stock(data_list)
            mo_id = mo['mo_id']
            material_id = mo['material_id']
            #参考生产工单进行生产入库
            #production_into_warehouse(data_list)

            #与生产工单关联的SO(关联或手绑销售订单)
            #so = sales_order.retrieve(data_list[1])
            #so_id = so.json()['content'][0]['id']
            #so_detail = sales_order.get_detail({'so_id': so_id})
            #生产工单信息查询
            # mo_no = data_list[0]['生产工单号']
            # body = {
            #     "kitting_status": 0,
            #     "pp_sn": mo_no,
            #     "need_update_bom": False,
            #     "production_plan_status": [0,10],
            #     "size": 20,
            #     "page": 0
            # }
            # mo = work_order.retrieve(body)
            # mo_id = mo.json()['content'][0]['id']
            # material_id = mo.json()['content'][0]['material_id']
            #与该生产工单关联的物料待出库数量(即已入库数量)
            #qty = mo.json()['content'][0]['shipped_qty']
            #先使用自定义退库数量，便于多次测试
            qty = data_list[4]['数量']
            #若生产工单是关联销售订单
            #mo_detail = work_order.get_detail({"production_plan_id":mo_id})
            #so_no = mo_detail.json()['document_no']
            #so = sales_order.retrieve({"so_query":so_no})
            #so_id = so.json()['content'][0]['id']

        #出库操作(退库)
            item = commons.dict_add(
                    {
                        "material_id": material_id,
                    #"mo_no": data_list[0]['生产工单号'],
                        "id": mo_id,
                        #"ref_no": data_list[0]['生产工单号'],
                        "ref_id": mo_id,
                        "ref_type": "MO",
                        "ref_item_id": mo_id,
                        "qty": qty,
                        "source_stock_type": "UU",
                        #"source_special_stock": True,
                        "source_special_stock": False,
                        #"source_special_stock_type": "Q",
                        #"source_special_stock_ref_type": "SO",
                        #"source_special_stock_ref_id": so_id
                    }, get_source_bin_info_4_warehouse_movement(data_list[3])
            )
            body = commons.dict_add({
                "ref_type": "MO",
                "stock_type": "UU",
                "order_mode": "RHM",
                "move_reason_code": "NA",
                "move_reason_desc": "正常操作",
                "items": [item]
            }, get_plant_info(), get_source_warehouse_info_4_warehouse_movement(data_list[3]), get_move_type(data_list[4]))

            r = goods_movement.create(body)
            assert(len(r.json()['id']) > 0)
            doc_id = r.json()['id']
        
            # 校验物料凭证存在
            material_doc_info = material_doc.get_detail({'material_doc_id': doc_id})
            assert(r.status_code == 200)
            assert(dict(material_doc_info.json()).__contains__('material_doc'))


    # #生产入库(待用)
    # def production_into_warehouse(mo):
        
    #     #生产工单信息查询
    #     # mo_no = data_list[0]['生产工单号']
    #     # body = {
    #     #     "kitting_status": 0,
    #     #     "pp_sn": mo_no,
    #     #     "need_update_bom": False,
    #     #     "production_plan_status": [
    #     #         0,
    #     #         10
    #     #     ],
    #     #     "size": 20,
    #     #     "page": 0
    #     # }
    #     # mo = work_order.retrieve(body)
        
    #     #从完工的MO中获取mo_id和material_id
    #     mo_id = mo.json()['id']
    #     material_id = mo.json()['material_id']

    #     #若生产工单是关联销售订单
    #     mo_detail = work_order.get_detail({"production_plan_id": mo_id})
    #     so_no = mo_detail.json()['document_no']
    #     so = sales_order.retrieve({"so_query": so_no})
    #     so_id = so.json()['content'][0]['id']
    #     #每次生产入库1,便于测试
    #     qty = 1
    #     #qty = mo.json()['content'][0]['shipped_qty']
    #     item = commons.dict_add({
    #         "material_id": material_id,
    #         "id": mo_id,
    #         #"mo_no": mo_no,
    #         #"ref_no": mo_no,
    #         "ref_id": mo_id,
    #         "ref_type": "MO",
    #         "ref_item_id": mo_id,
    #         "qty": qty,
    #         "destination_stock_type": "UU",
    #         "destination_special_stock": False,
    #         #"destination_special_stock_type": "Q",
    #         #"destination_special_stock_ref_type": "SO",
    #         #"destination_special_stock_ref_id": so_id
    #     }, get_bin_info_4_warehouse_movement(data_list[2]))
    #     body = commons.dict_add({
    #         "move_type_id": "b9d64f3e2d4011ea978d00505634f437",
    #         "move_type_no": "131",
    #         "move_type_desc": "131-生产工单入库",
    #         "ref_type": "MO",
    #         "stock_type": "UU",
    #         "order_mode": "RHM",
    #         "move_reason_code": "NA",
    #         "move_reason_desc": "正常操作",
    #         "items": [item]
    #     }, get_plant_info(), get_warehouse_info_4_warehouse_movement(data_list[2]))

    #     r = goods_movement.create(body)
    #     assert(len(r.json()['id']) > 0)
    #     doc_id = r.json()['id']

    #     # 校验物料凭证存在
    #     material_doc_info = material_doc.get_detail({'material_doc_id': doc_id})
    #     assert(r.status_code == 200)
    #     assert(dict(material_doc_info.json()).__contains__('material_doc'))



    #其他入库/232-销售出库-退库
    class Sale_out_stock_return_goods(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/232-销售出库-退库', text)
        def run(self):
            warehousing_by_other_ways_with_so(self.case_data["数据"],'RETURN SRSO')
            # #根据已创建订单，先执行一次销售出库操作(total_qty:8, out_qty:3，qty是和SO关联的库存数量，真实库存不一定是这么多)
            # #out_warehouse_sale_with_so(self.case_data["数据"])
            
            # #根据已关联的SO，查询出已发运/未发运(待入/总数)
            # so = sales_order.retrieve(self.case_data['数据'][0])
            # so_id = so.json()['content'][0]['id']
            # so_detail = sales_order.get_detail({'so_id': so_id})
            # completed_qty =  so_detail.json()['products'][0]['completed_qty']   #已发运数量 = 待入数量 = 需入库数量
            # ref_item_id = so_detail.json()['products'][0]['id']

            # #根据关联的SO，执行一次232-销售出库-退货操作（其他入库操作）
            # #填写入库数量 = 待入数量 = 已发运数量
            # data_list = self.case_data["数据"]

            #  # 入库api的请求体
            # ref_id = so_detail.json()['id']
            # ref_no = so_detail.json()['batch_no']
            # ref_type = 'SO'  # 关联SO
            # item = commons.dict_add({
            #     'material_id': material.get_field_by_name(data=data_list[2], filed_name='id'),
            #     "qty": completed_qty,
            #     #"completed_qty": completed_qty,
            #     "ref_item_id":ref_item_id,   
            #     "destination_stock_type": "UU",  # code def
            #     "destination_special_stock": True,
            #     "destination_special_stock_type": "Q",
            #     "destination_special_stock_ref_type": ref_type,
            #     "destination_special_stock_ref_id": ref_id
            # }, get_bin_info_4_warehouse_movement(data_list[1]))
            # body = commons.dict_add({
            #     "ref_no": ref_no,
            #     "ref_id": ref_id,
            #     "ref_type": ref_type,
            #     "move_reason_code": "NA",
            #     "move_reason_desc": "正常操作",
            #     "items": [item]
            # }, get_plant_info(), get_warehouse_info_4_warehouse_movement(data_list[1]), get_move_type(data_list[2]))

            # r = goods_movement.create(body)
            # assert(len(r.json()['id']) > 0)
            # doc_id = r.json()['id']
        
            # # 校验物料凭证存在
            # material_doc_info = material_doc.get_detail({'material_doc_id': doc_id})
            # assert(r.status_code == 200)
            # assert(dict(material_doc_info.json()).__contains__('material_doc'))
            # # 校验退货操作入库后SO的待入数(==0)
            # so_after = sales_order.retrieve(self.case_data['数据'][0])
            # so_after_id = so_after.json()['content'][0]['id']
            # so_after_detail = sales_order.get_detail({'so_id': so_after_id})
            # completed_after_qty =  so_after_detail.json()['products'][0]['completed_qty']
            # assert(completed_after_qty == 0)


    #其他出库/601-销售发运出库
    class Out_stock_by_sale_transport(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/601-销售发运出库', text)
        def run(self):
            move_type_no = self.case_data['数据'][1]['移动类型编号']
            #若租户没有该移动类型，则跳过
            check_move_type_exists(move_type_no,'SO')
            #out_warehouse_sale_with_so(self.case_data["数据"])
            oos_by_other_ways_with_so(self.case_data["数据"])


    #其他出库/203-售后出库
    class Sale_after_out_warehouse(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/203-售后出库', text)
        def run(self):
            move_type_no = self.case_data['数据'][1]['移动类型编号'] #FIXME  self.case_data['数据'][1] not self.case_data['数据'][2]
            #若租户没有该移动类型，则跳过
            check_move_type_exists(move_type_no,'SO')
            #out_warehouse_sale_with_so(self.case_data['数据'])
            oos_by_other_ways_with_so(self.case_data["数据"])

    # 其他出库/203-售后出库（不关联SO）
    class Oos_af_sales_without_so(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/203-售后出库/不关联SO', text)
        def run(self):
            warehousing_by_other_ways_without_so(self.case_data["数据"])

    # 204-售后出库退回
    class Warehousing_ref_ck_order(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/204-售后出库退回', text)
        def run(self):
            warehousing_by_other_ways_ref_to(self.case_data["数据"])

    # 541 
    class Warehousing_ref_outsourcing_po(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/541-委外订单入库', text)
        def run(self):
            warehousing_by_other_ways_with_po(self.case_data["数据"],'OUTSOURCING PO')

    class Entrust_external_order_out_warehouse(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/542-委外订单出库', text)
        def run(self):
            move_type_no = self.case_data['数据'][1]['移动类型编号']
            #若租户没有该移动类型，则跳过
            check_move_type_exists(move_type_no,'PO')
            #out_warehouse_sale_with_so(self.case_data['数据'])
            oos_by_other_ways_with_po(self.case_data["数据"],"OUTSOURCING PO")





    #其他出库/512-赠品入库退货
    class Giveaway_into_stock_return_goods(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/512-赠品入库退货', text)
        def run(self):
            move_type_no = self.case_data['数据'][1]['移动类型编号']
            #若租户没有该移动类型，则跳过
            check_move_type_exists(move_type_no,'SO')
            #out_warehouse_sale_with_so(self.case_data['数据'])
            oos_by_other_ways_with_so(self.case_data["数据"])

    class Out_stock_initial_return_goods(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/812-期初初始退货', text)
        def run(self):
            move_type_no = self.case_data['数据'][1]['移动类型编号']
            #若租户没有该移动类型，则跳过
            check_move_type_exists(move_type_no,'SO')
            #out_warehouse_sale_with_so(self.case_data['数据'])
            oos_by_other_ways_with_so(self.case_data["数据"])


    #库存转移(从源仓库选择一条库存转移到目标仓库)
    class Stock_material_move(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/库存转储/库存转移', text)

        def run(self):
            material_list = material.retrieve(self.case_data['数据'][2])
            material_id = material_list.json()['content'][0]['id']
            material_no = material_list.json()['content'][0]['material_no']
            
            source_warehouse = warehouse.get_warehouse_no({"warehouse_no":self.case_data['数据'][0]['源仓库编号']})
            #源仓库基本信息
            source_warehouse_id = source_warehouse.json()[0]['id']
            source_warehouse_no = source_warehouse.json()[0]['warehouse_no']
            source_warehouse_name = source_warehouse.json()[0]['warehouse_no_name']
            #源仓库库存地点信息
            source_storage_location_id = source_warehouse.json()[0]['storage_locations'][0]['id']
        # plant_id = source_warehouse.json()[0]['storage_locations'][0]['plant_id']
            source_storage_location_name = source_warehouse.json()[0]['storage_locations'][0]['storage_location_name']
            source_storage_location_name = source_warehouse.json()[0]['storage_locations'][0]['storage_location_name']
        
            target_warehouse = warehouse.get_warehouse_no({"warehouse_no":self.case_data['数据'][1]['目标仓库编号']})       
            #目标仓库基本信息
            target_warehouse_id = target_warehouse.json()[0]['id']
            target_warehouse_no = target_warehouse.json()[0]['warehouse_no']
            target_warehouse_name = target_warehouse.json()[0]['warehouse_no_name']
            #目标仓库库存地点信息
            target_storage_location_id =  target_warehouse.json()[0]['storage_locations'][0]['id']
            target_storage_location_name = target_warehouse.json()[0]['storage_locations'][0]['storage_location_name']
            #获取目标仓库库位信息
            target_warehouse_bin_info = warehouse.get_warehouse_bin_info({"storage_bin_no":self.case_data['数据'][1]['目标仓库库位']})
            
            #转存之前查询源仓库库存信息
            source_param_before = {
                "material_id":material_id,
                "material_no":material_no,
                "warehouse_id":source_warehouse_id,
                "special_stock_type":"COMMON",
                "empty_lot_name":False
            }
            source_warehouse_result_before = stock.retrieve_bin_stock_list(source_param_before)
            source_bin_id = source_warehouse_result_before.json()[0]['storage_bin_id']
            source_bin_no = source_warehouse_result_before.json()[0]['storage_bin_no']
            stock_type = source_warehouse_result_before.json()[0]['stock_type']
            #源仓库某物料原有库存数量()
            source_total_quantity_before = source_warehouse_result_before.json()[0]['total_quantity']
            
            #转存之前查询目标仓库库存信息
            target_param_before = {
                "material_id":material_id,
                "material_no":material_no,
                "warehouse_id":target_warehouse_id,
                "special_stock_type":"COMMON",
                "empty_lot_name":False
            }
            target_warehouse_result_before = stock.retrieve_bin_stock_list(target_param_before)
            item = {
                    "source_bin_id": source_bin_id,
                    "source_bin_no": source_bin_no,                      
                    "source_stock_type": stock_type,
                    "material_id": material_id,
                    "qty": self.case_data['数据'][1]['移动数量'],            #转存数量
                    "source_special_stock": False,
                    "destination_bin_id": target_warehouse_bin_info.json()['content'][0]['id'], 
                    "destination_bin_no": self.case_data['数据'][1]['目标仓库库位'],               
                    "destination_stock_type": self.case_data['数据'][1]['目标库存类型'],          
                    "destination_special_stock": False
                }
            body = commons.dict_add({
                "charge_cost_center": False,
                "charge_project": False,
                "move_reason_code": "NA",
                "move_reason_desc": "正常操作",
                "lot_transfer_mode": "TRANSFER",
                "source_storage_location_id": source_storage_location_id,
                "source_storage_location_name": source_storage_location_name,     
                "source_warehouse_id": source_warehouse_id,
                "source_warehouse_name": source_warehouse_name,                    
                "source_warehouse_no": source_warehouse_no,

                "destination_storage_location_id": target_storage_location_id,
                "destination_storage_location_name": target_storage_location_name,   #目标仓库库存地点（根据所有仓库自动选择）
                "destination_warehouse_id": target_warehouse_id,
                "destination_warehouse_name": target_warehouse_name,                
                "destination_warehouse_no": target_warehouse_no,                     
                "items":[item]     
            },get_plant_info(),get_move_type(self.case_data['数据'][2]))
            r = stock.update(body)
            assert(len(r.json()['id']) > 0)
            doc_id = r.json()['id']
            # 校验物料凭证存在
            material_doc_info = material_doc.get_detail({'material_doc_id': doc_id})
            assert(r.status_code == 200)
            assert(dict(material_doc_info.json()).__contains__('material_doc'))

            #校验(分别验证源仓库和目标仓库)
            sorece_param_after = {
                "material_id":material_id,
                "material_no":material_no,
                "warehouse_id":source_warehouse_id,
                "special_stock_type":"COMMON",
                "empty_lot_name":False
            }
            source_warehouse_result_after = stock.retrieve_bin_stock_list(sorece_param_after)
            
            #移动数量小于库存数量,源仓库库存减少，目标仓库库存增加
            source_total_quantity_after = source_warehouse_result_after.json()[0]['total_quantity']
            #校验源仓库库存数量
            assert (source_total_quantity_after <= source_total_quantity_before)
            
            #根据目标仓库原来是否有该物料进行结果校验
            target_param_after = {
                "material_id":material_id,
                "material_no":material_no,
                "warehouse_id":target_warehouse_id,
                "special_stock_type":"COMMON",
                "empty_lot_name":False
            }
            target_warehouse_result_after = stock.retrieve_bin_stock_list(target_param_after)
            target_total_quantity_after = target_warehouse_result_after.json()[0]['total_quantity']        
            # if target_warehouse_result_before:
            #     target_total_quantity_before = target_warehouse_result_before.json()[0]['total_quantity']
            #     assert((target_total_quantity_after - target_total_quantity_before) == self.case_data['数据'][1]['移动数量'])
            # else:
            #     assert(target_total_quantity_after == self.case_data['数据'][1]['移动数量'])

        
            
        
            #assert (len(r.json()['content']) >= self.case_data['期望校验数据'][0])
    class other_store_out_return_order(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他出库/退货订单/121-退货', text)

        #现在的po的创建后需要被审批后才可以在退货中选择po订单 --TODO
        def run(self):
            oos_by_other_ways_with_po(self.case_data["数据"])
            
    class out_in_stock_detail_query(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/出入库明细查询/查询', text)

        def run(self):
            move_type_code = self.case_data['数据'][0]['业务类型']
            store = out_in_stock.retrieve({"move_type_code" : move_type_code})

            assert (store.status_code == 200)
            assert (len(store.json()['content']) > 0)

    class other_storage_with_so_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/264-依据SO入库（参考261）', text)

        def run(self):
            warehousing_by_other_ways_with_so(self.case_data["数据"],"COMMON TO")

    class other_storage_scrap_out_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/552-报废出库（取消)', text)

        @allure.step
        def run(self):
            warehousing_by_other_ways_with_so(self.case_data["数据"])

    class other_storage_sale_shipped_refund_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/602-销售发运退库', text)
        
        @allure.step
        def run(self):
            warehousing_by_other_ways_with_so(self.case_data["数据"])


        
    class export_arrival_order(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/到货单/导出', text) 
        
        def run(self):
            # 查询到货单明细列表,并获取到货单明细总数
            # 此处为默认过滤条件
            order_type="CGDHD"
            status="O"
            data={"order_type":order_type,"status":status,"finish_status":[0,1]}
            r=arrived_order.detail_retrieve(data)
            assert r.status_code == 200
            total_elements=r.json()["total_elements"]
            #传入筛选条件给导出到货单接口
            # 此处为默认过滤条件
            data={"order_type":order_type,"status":[status],"finish_status":[0,1]}
            r=bc_task.export_arriver_order_items(data)
            assert r.status_code ==200
            #查询任务中心新建的到货单导出任务->查询成功->校验
            r=task.retrieve({"size": 20,"page": 0})
            assert r.status_code ==200
            #根据已有的任务列表，找到刚刚创建的导出任务
            #最简单的方式，按照导出任务的第一个"到货单明细导出"任务
            id=""
            for items in r.json()["content"]:
                if items["name"] == "到货单明细导出":
                    id=id+items["id"]
                    break
            #比较接近实际的方式，根据时间比较判断
            #任务成功->获取导出文件地址exportFileUrl->校验
            status="CREATED"
            print(id)
            while status == "CREATED":
                time.sleep(5)#考虑到可能查询时候任务未完成，设置5秒一查
                r=task.retrieve({"size": 20,"page": 0})
                for items in r.json()["content"]:
                    if items["id"]==id:
                        if items["status"]=="CREATED":
                            break
                        elif items["status"]=="EXECUTING":
                            break
                        elif items["status"]=="SUCCEEDED":
                            status="SUCCEEDED"
                            exportFileUrl=items["extra"]["exportFileUrl"]   
                            break
                        else:
                            Logger.info("任务创建失败")
                            pytest.fail()
            #下载导出文件，并与到货单明细数量对比
            #判断是否在result存在download_files目录
            task.check_export_task(exportFileUrl,"到货单明细导出.xlsx",total_elements)
            '''
            task.download_file(exportFileUrl,"result/download_files/到货单明细导出.xlsx")#该方法用于下载文件并存放在指定的本地目录中
            with warnings.catch_warnings(record=True):#屏蔽告警：若不加这个会报：with warnings.catch_warnings(record=True)，不屏蔽不影响运行通过
                wb=load_workbook("result/download_files/到货单明细导出.xlsx")
                sheets = wb.worksheets
                sheet1 = sheets[0]
                rows=sheet1.max_row
            assert total_elements==rows-1
            '''

    class create_pick_order(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/工单领料/新建领料单', text)
        
        def run(self):
            #建立工单并下发,获取创建的工单id
            mo_id=Create_work_order(self.case_data['数据'])["mo_id"]
            #将创建的mo的id放到global data中，此处存在一个情况，在仓库管理整个流程中涉及到工单的部分，工单领料的顺序应该最靠前，所以在新建领料单创建的工单可由新建退料单、工单完工入库使用，所以当global data在执行该用例之前应不存在关联的mo信息
            if global_data.data.__contains__("wm") :
                global_data.data['wm']['mo_id'] = mo_id
            else :
                global_data.data['wm']={"mo_id":mo_id}

            #根据给定的工单id，获取工单BOM合并之后的物料
            #获取两个参数，总共数量和自制发货库存地点的id
            r=material_pick.material_in_workorder_retrieve({"moIds":[mo_id]})
            assert r.status_code ==200
            total_quantity=r.json()[0]["total_quantity"]
            picking_storage_location_id=r.json()[0]["picking_storage_location_id"]
            material_id=r.json()[0]["material_id"]
            data={}
            data["items"]=r.json()
            #默认需要领全部量的料，提交->获取领料单id->校验
            required_qty=total_quantity
            max_qty=total_quantity
            storage_location_id=picking_storage_location_id
            data["items"][0]["required_qty"]=required_qty
            data["items"][0]["max_qty"]=max_qty
            data["items"][0]["storage_location_id"]=storage_location_id
            data["mo_ids"]=[mo_id]
            data["items"][0]["priority"]=None
            r=material_pick.pickorder_create(data)
            assert r.status_code ==200
            pick_order_id=r.json()[0]["id"]
            global_data.data['wm']["pick_material_order_id"]=pick_order_id
            #在领退料列表查询，领料单类型选择“领料单”，工单号为指定工单号，状态为已创建->查询到领料单，比较领料单id是否一致
            data=self.case_data['数据'][0]
            data["order_type"]="SCLLD"
            data["status"]="O"
            data["finish_status"]=[0,1]
            data["tr_type"]=313
            r=material_pick.retrieve(data)
            assert r.status_code==200
            assert pick_order_id==r.json()["content"][0]["id"]
            #根据获得的领料单id查询领料单，比较是否数据一致
            r=material_pick.get_detail({"tr_id":pick_order_id,"only_positive":True})
            assert r.json()["mo_links"][0]["mo_id"]==mo_id
            data=   {
                        "material_id":material_id,
                        "total_quantity":total_quantity,
                        "complete_quantity":0,
                        "open_quantity":total_quantity,
                        "storage_location_id":storage_location_id
                    }
            self.compare_result_detail(data,r.json()["tr_items"][0])
            
    class pick_material(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/工单领料/领料', text) 
        
        def run(self):
            #前置：创建一个领料单，且物料在仓库内有足够数量可以领取
            #在领退料列表查询，领料单类型选择“领料单”，工单号为指定工单号，状态为已创建->查询到领料单，获取领料单id(该步骤取消)
            
            #global_data获取已创建的领料单id，若没有，则说明新建领料单步骤未执行或失败
            if global_data.data.__contains__("wm") and global_data.data["wm"].__contains__("pick_material_order_id"):
                pick_order_id=global_data.data['wm']['pick_material_order_id']
            else :
                Logger.info("未执行新建领料单步骤或新建领料单步骤执行失败")
                pytest.fail()
            '''
            data=self.case_data['数据'][0]
            data["order_type"]="SCLLD"
            data["status"]="O"
            data["finish_status"]=[0,1]
            data["tr_type"]=313
            r=material_pick.retrieve(data)
            assert r.status_code==200
            pick_order_id=r.json()["content"][0]["id"]
            ref_no=r.json()["content"][0]["tr_no"]
            '''
            #验证领料单是否有效
            r=material_pick.validate_pick_list({"tr_id":pick_order_id})
            if r.json()["result"] != True:
                Logger.info("领料单无效")
                pytest.fail() 
            #查看当前领料单详情->获取必要参数->校验
            r=material_pick.get_detail({"tr_id":pick_order_id,"only_positive":True})
            assert r.status_code ==200
            ref_no=r.json()["tr_no"]
            storage_location_id=r.json()["tr_items"][0]["storage_location_id"] #先按照默认一个物料需要领
            storage_location_name=r.json()["tr_items"][0]["storage_location_name"]
            material_id=r.json()["tr_items"][0]["material_id"]
            if r.json()["so_no"]=="":#若未关联so，则赋予一个状态值
                isRefSO = False
            else:
                isRefSO = True
            if isRefSO == True:
                so_id=r.json()["tr_items"][0]["so_id"]
                so_no=r.json()["tr_items"][0]["so_no"]
            response_get_detail=r.json()["tr_items"]
            #获取所有可以出库的仓库和库位，并查看是否领料单中选择的仓库可以出库
            r=material_pick.retrieve_warehouse_location({"exclude_forbidden_out":True})
            assert r.status_code ==200
            warehouse=[]
            plant_ids=[]
            judge=0
            for items in r.json():
                if  "storage_locations" in items and items["storage_locations"][0]["id"]==storage_location_id:
                    warehouse.append(items["id"])
                    warehouse.append(items["warehouse_no"])
                    warehouse.append(items["warehouse_no_name"])
                    plant_ids.append(items["storage_locations"][0]["plant_id"])
                    judge=1
                    break
            #若领料单所填仓库允许出库，则使用该仓库出库
            if judge ==0:
                Logger.error("选择的仓库无法出库")
                pytest.fail()
            #根据所选的库存地点，查询得到库位
            warehouse_no=warehouse[1]
            stock_type="UU"
            if isRefSO == True:#关联销售订单的情况下，查询需要带上so的信息，否则不需要
                r=material_pick.have_material_location({"materialSoVOS":[{"material_id":material_id,"so_no":so_no,"so_id":so_id}],"stock_type":stock_type,"warehouse_no":warehouse_no})
            else:
                r=material_pick.have_material_location({"materialSoVOS":[{"material_id":material_id}],"stock_type":stock_type,"warehouse_no":warehouse_no})
            assert r.status_code == 200
            storage_bin_no=r.json()[0][0]["storage_bin_no"]#此处先为一个库位有该物料
            response_have_material_location=r.json()[0]
            #提交所需参数->获取领料id->校验
            response_get_detail[0]["bins"]=response_have_material_location
            response_get_detail[0]["bin_id"]=response_get_detail[0]["bins"][0]["id"]
            response_get_detail[0]["quantity"]=response_get_detail[0]["open_quantity"]
            response_get_detail[0]["material"]={"id":response_get_detail[0]["material_id"],"material_no":response_get_detail[0]["material_no"]}
            response_get_detail[0]["material_id"]=response_get_detail[0]["material_id"]
            response_get_detail[0]["material_no"]=response_get_detail[0]["material_no"]
            response_get_detail[0]["material_name"]=response_get_detail[0]["material_name"]
            response_get_detail[0]["material_desc"]=response_get_detail[0]["material_desc"]
            response_get_detail[0]["available_stock"]=response_get_detail[0]["bins"][0]["available_stock"]
            response_get_detail[0]["has_child"]=False       
            response_get_detail[0]["sequence"]=1
            response_get_detail[0]["summary_quantity"]=None
            response_get_detail[0]["stock_negative_allowed"]=False
            response_get_detail[0]["select"]=False
            response_get_detail[0]["is_hide"]=False
            response_get_detail[0]["supplier_id"]=None
            response_get_detail[0]["ref_item_no"]=None
            response_get_detail[0]["ref_item_numc"]=None
            response_get_detail[0]["lot_name"]=None
            response_get_detail[0]["field_values"]=None
            response_get_detail[0]["unit_name"]=None
            response_get_detail[0]["bin_no"]=response_get_detail[0]["bins"][0]["storage_bin_no"]
            response_get_detail[0]["stock_type"]="UU"
            response_get_detail[0]["ref_id"]=pick_order_id
            response_get_detail[0]["ref_no"]=ref_no
            response_get_detail[0]["ref_type"]="TR"
            response_get_detail[0]["ref_item_id"]=response_get_detail[0]["id"]
            response_get_detail[0]["source_bin_id"]=response_get_detail[0]["bins"][0]["id"]
            response_get_detail[0]["source_bin_no"]=response_get_detail[0]["bins"][0]["storage_bin_no"]
            response_get_detail[0]["source_stock_type"]="UU"
            if isRefSO==True:
                response_get_detail[0]["source_so_no"]=so_no
                response_get_detail[0]["source_so_id"]=so_id
                response_get_detail[0]["source_special_stock"]=True
                response_get_detail[0]["source_special_stock_type"]="Q"
                response_get_detail[0]["source_special_stock_ref_type"]="SO"
                response_get_detail[0]["source_special_stock_ref_id"]=so_id
            else:
                response_get_detail[0]["so_no"]=None
                response_get_detail[0]["so_id"]=None
                response_get_detail[0]["source_special_stock"]=False
                response_get_detail[0]["source_special_stock_type"]=None
                response_get_detail[0]["source_special_stock_ref_type"]=None
                response_get_detail[0]["source_special_stock_ref_id"]=None
            response_get_detail[0]["qty"]=response_get_detail[0]["open_quantity"]
            plant_id=plant_ids[0]#遗留一个问题：如何查出工厂名字
            warehouse_id=warehouse[0]
            warehouse_no_name=warehouse[2]
            data={
                    "ref_no":ref_no,
                    "ref_id":pick_order_id,
                    "ref_type":"TR",
                    "remark":None,
                    "used_unit":None,
                    "move_type_id":None,
                    "move_type_no":"313",
                    "move_type_desc":"313-领料到产线",
                    "warehouse_id":warehouse_id,
                    "warehouse_no":warehouse_no,
                    "warehouse_name":warehouse_no_name,
                    "source_warehouse_id":warehouse_id,
                    "source_warehouse_no":warehouse_no,
                    "source_warehouse_name":warehouse_no_name,
                    "destination_warehouse_id":None,
                    "destination_warehouse_no":None,
                    "destination_warehouse_name":None,
                    "stock_type":"UU",
                    "order_mode":"RIS",
                    "doc_at":None,
                    "move_type_config_id":None,
                    "move_reason_code":"NA",
                    "move_reason_desc":"正常操作",
                    "storage_location_id":storage_location_id,
                    "storage_location_name":storage_location_name,
                    "source_storage_location_id":storage_location_id,
                    "source_storage_location_name":storage_location_name,
                    "destination_storage_location_id":None,
                    "destination_storage_location_name":None,
                    "is_hide_data":False,
                    "request_by":None,
                    "org_id":None,
                    "items":response_get_detail,
                    "plant_id":plant_id,
                    "plant_name":'plant_name'#FIXME
                }
            parms={"tr_id":pick_order_id,"data":data}
            r=material_pick.pick_material(parms)
            assert r.status_code ==200
            material_doc_id=r.json()["id"]
            #封装校验数据，跳转到领料凭证进行校验
            r=material_pick.pick_check({"material_doc_id":material_doc_id})
            assert r.status_code ==200
            if isRefSO==True:
                check_data={
                "ref_id":pick_order_id,
                "plant_id":plant_id,
                "warehouse_id":warehouse_id,
                "storage_location_id":storage_location_id,
                "storage_bin_id":response_get_detail[0]["source_bin_id"],
                "move_type_id":response_get_detail[0]["move_type_id"],
                "move_type_no":response_get_detail[0]["move_type_no"],
                "move_reason_code":parms["data"]["move_reason_code"],
                "material_id":response_get_detail[0]["material_id"],
                "stock_type":"UU",
                "special_stock" : True,
                "special_stock_type":"Q",
                "special_stock_ref_type":"SO",
                "so_id":so_id,
                "auxiliary_quantity":response_get_detail[0]["qty"]
                } 
            else:
                check_data={
                "ref_id":pick_order_id,
                "plant_id":plant_id,
                "warehouse_id":warehouse_id,
                "storage_location_id":storage_location_id,
                "storage_bin_id":response_get_detail[0]["source_bin_id"],
                "move_type_id":response_get_detail[0]["move_type_id"],
                "move_type_no":response_get_detail[0]["move_type_no"],
                "move_reason_code":parms["data"]["move_reason_code"],
                "material_id":response_get_detail[0]["material_id"],
                "stock_type":"UU",
                "special_stock" : False,
                "auxiliary_quantity":response_get_detail[0]["qty"]
                }
            self.compare_result_detail(check_data,r.json()["items"][0])


# class other_store_out_with_so_ok(Abstract_case):

#      #此264类型其他出库中没有--TODO

#     def __init__(self, text=None) -> None:
#         super().__init__('仓库管理/其他出库/264-依据SO入库（参考261）', text)
    
#     def run(self):
#         oos_by_other_ways_with_so(self.case_data["数据"])



    # class other_store_out_with_so_ok(Abstract_case):

    #      #此264类型其他出库中没有--TODO

    #     def __init__(self, text=None) -> None:
    #         super().__init__('仓库管理/其他出库/264-依据SO入库（参考261）', text)
        
    #     def run(self):
    #         oos_by_other_ways_with_so(self.case_data["数据"])


    class other_store_out_abnormal_picking_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__("仓库管理/其他出库/275-完工后异常领料", text)

        def run(self):
            #暂时先把so写死 之后可能会有生成so的方法统一调用
            so_id = "77a0fa5654ef4eb1a7c66bed68d333d2"
            so_no = "SO20210906000036"
            oos_by_other_ways_with_so(self.case_data["数据"])

    class other_store_out_scrap_out_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__("仓库管理/其他出库/551-报废出库", text)

        def run(self):
            oos_by_other_ways_with_so(self.case_data["数据"])


    class other_store_out_deplete_with_so_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__("仓库管理/其他出库/261-根据SO消耗", text)
        def run(self):
            material_doc_info = oos_by_other_ways_with_so(self.case_data["数据"])
            
            #将创建生成的出库单号CK存入global_data，给264-依据SO入库（参考261）使用
            material_doc_id = material_doc_info.json()["material_doc"]["id"] 
            global_data.data['wm']={"material_doc_id" : material_doc_id}  

            return material_doc_id

    class other_store_out_borrow_material_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__("仓库管理/其他出库/712-借料", text)
        def run(self):
            oos_by_other_ways_with_so(self.case_data["数据"])



    class Create_return_order_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__("仓库管理/工单退料/新建退料单", text)
        def run(self):
        #前置：建立工单并释放，先新建一个工单领料，然后才有数量可退
        
            #从global_data中获取工单领料/新建领料单时创建的mo_id
            mo_id = global_data.data['wm']['mo_id']
            #根据给定的工单id，获取工单BOM合并之后的物料
            #获取两个参数，总共数量和自制发货库存地点的id
            r=material_return.material_in_workorder_retrieve({"moIds":[mo_id]})
            assert r.status_code ==200
            complete_quantity=r.json()[0]["complete_quantity"]
            total_quantity=r.json()[0]["total_quantity"]
            picking_storage_location_id=r.json()[0]["picking_storage_location_id"]
            material_id=r.json()[0]["material_id"]
            

            # #默认全部退料，提交->获取退料单id->校验
            # required_qty=complete_quantity
            # max_qty=complete_quantity
            # storage_location_id=picking_storage_location_id
            # data["items"][0]["required_qty"]=required_qty
            # data["items"][0]["max_qty"]=max_qty
            # #data["items"][0]["storage_location_id"]=storage_location_id
            # data["mo_ids"]=[mo_id]
            # data["items"][0]["priority"]=None

            data={}
            data["items"]=r.json()
            #默认需要退全部量的料，提交->获取领料单id->校验
            required_qty=complete_quantity
            max_qty=total_quantity
            storage_location_id=picking_storage_location_id
            data["items"][0]["required_qty"]=required_qty
            data["items"][0]["max_qty"]=max_qty
            data["items"][0]["storage_location_id"]=storage_location_id
            data["mo_ids"]=[mo_id]
            data["items"][0]["priority"]=None

            r=material_return.return_order_create(data)
            assert r.status_code ==200
            return_order_id=r.json()[0]["id"]
            #把生成的工单退料单id放到global_data中
        
            if global_data.data.__contains__("wm") :
                global_data.data['wm']['return_order_id'] = return_order_id
            else :
                global_data.data['wm']={"return_order_id":return_order_id}

            #在领退料列表查询，类型选择“退料单”，工单号为指定工单号，状态为已创建->查询到退料单，比较退料单id是否一致
            data=self.case_data['数据'][0]
            data["order_type"]="SCTLD"
            data["status"]="O"
            data["finish_status"]=[0,1]
            data["tr_type"]=262            #查询退料单
            r=material_return.retrieve(data)
            assert r.status_code==200
            assert return_order_id==r.json()["content"][0]["id"]
            #根据获得的退料单id查询退料单，比较是否数据一致
            r=material_return.get_detail({"tr_id":return_order_id,"only_positive":True})
            assert r.json()["mo_links"][0]["mo_id"]==mo_id
            # data =   {
            #             "material_id":material_id,
            #             "total_quantity":total_quantity,
            #             "complete_quantity":0,
            #             "open_quantity":total_quantity,
            #             "storage_location_id":storage_location_id
            #         }
            # self.compare_result_detail(data,r.json()["tr_items"][0])

    class Query_return_order_detail(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__("仓库管理/工单退料/详情", text)
        def run(self):
            # data = self.case_data['数据'][0]
            # data["order_type"] = "SCTLD"
            # data["status"] = "O"
            # data["finish_status"] = [0, 1]
            # data["tr_type"] = 262
            # r = material_return.retrieve(data)
            # assert(r.status_code == 200)
            # assert(len(r.json()['content']) > 0)
            # id = r.json()['content'][0]['id']

            #从工单退料/新建退料单用例中获取退料单id
            tr_id = global_data.data['wm']['return_order_id']
            return_order_detail = material_return.get_detail({'tr_id': tr_id})
            assert(return_order_detail.status_code == 200)
            #验证详情信息中的退料单id
            #assert(return_order_detail.json()['mo_links'][0]['tr_id'] == tr_id)
        

    class work_order_return_material_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__("仓库管理/生产领料/工单退料/退料", text)

        def run(self):
            # tr_id = "38e0affda32549af92820c4b07116ba8"
            tr_id = global_data.data['wm']['return_order_id']
            pick_detail = material_return.get_detail({'tr_id': tr_id,"only_positive":True}).json()
            # assert(pick_detail.status_code == 200)
            tr_no = pick_detail['tr_no']

            bin_info = get_bin_info_4_warehouse_movement(self.case_data['数据'][0])
            warehouse_info = get_warehouse_info_4_warehouse_movement(self.case_data['数据'][0])
            plant_info = get_plant_info()

            #获取到destination_special_stock_ref_id ，通过so_no调用sd接口获取so_id
            so_no = pick_detail["so_no"]
            so_id = sales_order.retrieve({"so_query":so_no}).json()["content"][0]["id"]
            

            data = {
                "tr_id": tr_id,
                "ref_type":"TR",
                
                "move_type_no":"262",
                "move_type_desc":"262-生产领料-退货",
                "destination_warehouse_id":warehouse_info["destination_warehouse_id"], 
                "destination_warehouse_no":warehouse_info["destination_warehouse_no"],                                      
                "destination_warehouse_name":warehouse_info["destination_warehouse_name"],  
                "move_reason_code":"NA",
                "move_reason_desc":"正常操作",
                "destination_storage_location_id":warehouse_info["destination_storage_location_id"], 
                "destination_storage_location_name":warehouse_info["destination_storage_location_name"],
                "items":[
                {
                "material_id": pick_detail['tr_items'][0]['material_id'],
                "move_type_id": pick_detail['tr_items'][0]['move_type_id'],
                "move_type_no": pick_detail['tr_items'][0]['move_type_no'],
                "move_type_desc": pick_detail['tr_items'][0]['move_type_desc'],
                "qty":self.case_data['数据'][1]['出库数量'],
                "ref_item_id": pick_detail['tr_items'][0]['id'],
                "destination_bin_id":bin_info["destination_bin_id"],
                "destination_bin_no":bin_info["destination_bin_no"],
                "destination_stock_type":"UU",
                "destination_special_stock":True, 
                "destination_special_stock_type":"Q",
                "destination_special_stock_ref_type":"SO",
                "destination_special_stock_ref_id":so_id
                }
                ],
                "plant_id":plant_info["plant_id"],
                "plant_name":plant_info["plant_name"]
            }
            r = goods_movement.picking(data)
            assert(r.status_code == 200)
        
    
       
    class out_in_stock_export(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/出入库明细查询/导出', text) 
        
        def run(self):
            # 查询出入库明细列表,并获取出入库明细总数
            # 此处查询条件为：本月的第一天到当前时间作为开始和结束时间
            start_transfer_date=str(datetime.date.today().replace(day=1))
            end_transfer_date=str(datetime.date.today())
            data={"start_transfer_date":start_transfer_date,"end_transfer_date":end_transfer_date}
            r=out_in_stock.retrieve(data)
            assert r.status_code == 200
            total_elements=r.json()["total_elements"]
            #传入筛选条件给导出出入库明细接口
            # 此处查询条件为：本月的第一天到当前时间作为开始和结束时间
            r=bc_task.export_out_in_stock(data)
            assert r.status_code ==200
            #查询任务中心新建的到货单导出任务->查询成功->校验
            r=task.retrieve({"size": 20,"page": 0})
            assert r.status_code ==200
            #根据已有的任务列表，找到刚刚创建的导出任务
            #最简单的方式，按照导出任务的第一个"到货单明细导出"任务
            id=""
            for items in r.json()["content"]:
                if items["name"] == "出入库明细导出":
                    id=id+items["id"]
                    break
            #比较接近实际的方式，根据时间比较判断
            #任务成功->获取导出文件地址exportFileUrl->校验
            status="CREATED"
            print(id)
            while status == "CREATED":
                time.sleep(5)#考虑到可能查询时候任务未完成，设置5秒一查
                r=task.retrieve({"size": 20,"page": 0})
                for items in r.json()["content"]:
                    if items["id"]==id:
                        if items["status"]=="CREATED":
                            break
                        elif items["status"]=="EXECUTING":
                            break
                        elif items["status"]=="SUCCEEDED":
                            status="SUCCEEDED"
                            exportFileUrl=items["extra"]["exportFileUrl"]   
                            break
                        else:
                            Logger.info("任务创建失败")
                            pytest.fail()
            #下载导出文件，并与出入库明细数量对比
            task.check_export_task(exportFileUrl,"出入库明细导出.xlsx",total_elements)


    class Query_material_doc_export(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/物料凭证明细查询/导出', text) 
        
        def run(self):
            # 查询物料凭证明细列表,并获取物料凭证明细总数
            # 此处查询条件为：测试数据中所给的移动类型（和物料凭证明细查询的筛选条件同步）
            r = material_doc.retrieve_material_doc_detail(get_move_type(self.case_data['数据'][0]))
            assert r.status_code == 200
            total_elements=r.json()["total_elements"]
            #传入筛选条件给导出物料凭证明细接口
            # 此处查询条件为：测试数据中所给的移动类型
            move_type_id=get_move_type(self.case_data['数据'][0])["move_type_id"]
            r=bc_task.export_query_material_doc({"move_type_id":move_type_id})
            assert r.status_code ==200
            #查询任务中心新建的到货单导出任务->查询成功->校验
            r=task.retrieve({"size": 20,"page": 0})
            assert r.status_code ==200
            #根据已有的任务列表，找到刚刚创建的导出任务
            #最简单的方式，按照导出任务的第一个"到货单明细导出"任务
            id=""
            for items in r.json()["content"]:
                if items["name"] == "物料凭证明细导出":
                    id=id+items["id"]
                    break
            #比较接近实际的方式，根据时间比较判断
            #任务成功->获取导出文件地址exportFileUrl->校验
            status="CREATED"
            print(id)
            while status == "CREATED":
                time.sleep(5)#考虑到可能查询时候任务未完成，设置5秒一查
                r=task.retrieve({"size": 20,"page": 0})
                for items in r.json()["content"]:
                    if items["id"]==id:
                        if items["status"]=="CREATED":
                            break
                        elif items["status"]=="EXECUTING":
                            break
                        elif items["status"]=="SUCCEEDED":
                            status="SUCCEEDED"
                            exportFileUrl=items["extra"]["exportFileUrl"]   
                            break
                        else:
                            Logger.info("任务创建失败")
                            pytest.fail()
            #下载导出文件，并与出入库明细数量对比
            task.check_export_task(exportFileUrl,"物料凭证明细导出.xlsx",total_elements)

    class query_bin_stock_export(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/库位库存查询/明细导出', text) 
        
        def run(self):
            # 查询库位库存查询明细列表,并获取库位库存查询明细总数
            # 此处查询条件为：测试数据中所给的库存类型（和库位库存明细查询的筛选条件同步）
            stock_type = self.case_data['数据'][0]['库存类型']
            r = inventory.retrieve({"stock_type":stock_type})
            assert (r.status_code == 200)
            total_elements=r.json()["total_elements"]
            #传入筛选条件给导出库位库存明细导出接口
            # 此处查询条件为：测试数据中所给的库存类型
            r=bc_task.export_query_bin_stock({"stock_type":stock_type,"sort":["material_no,desc"]})
            assert r.status_code ==200
            #查询任务中心新建的到货单导出任务->查询成功->校验
            r=task.retrieve({"size": 20,"page": 0})
            assert r.status_code ==200
            #根据已有的任务列表，找到刚刚创建的导出任务
            #最简单的方式，按照导出任务的第一个"库位库存查询明细明细导出"任务
            id=""
            for items in r.json()["content"]:
                if items["name"] == "库位库存明细导出":
                    id=id+items["id"]
                    break
            #比较接近实际的方式，根据时间比较判断
            #任务成功->获取导出文件地址exportFileUrl->校验
            status="CREATED"
            print(id)
            while status == "CREATED":
                time.sleep(5)#考虑到可能查询时候任务未完成，设置5秒一查
                r=task.retrieve({"size": 20,"page": 0})
                for items in r.json()["content"]:
                    if items["id"]==id:
                        if items["status"]=="CREATED":
                            break
                        elif items["status"]=="EXECUTING":
                            break
                        elif items["status"]=="SUCCEEDED":
                            status="SUCCEEDED"
                            exportFileUrl=items["extra"]["exportFileUrl"]   
                            break
                        else:
                            Logger.info("任务创建失败")
                            pytest.fail()
            #下载导出文件，并与库位库存查询明细总数对比
            task.check_export_task(exportFileUrl,"库位库存明细导出.csv",total_elements)

    class total_stock_export(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/库位库存查询/汇总导出', text) 
        
        def run(self):
            # 查询库位库存查询汇总列表,并获取库位库存查询汇总总数
            # 此处查询条件为：测试数据中所给的库存地点和物料（和库位库存汇总查询的筛选条件同步）
            material_list = material.retrieve({"material":self.case_data['数据'][0]['物料名称']})
            material_id = material_list.json()['content'][0]['id']
            material_no = material_list.json()['content'][0]['material_no']              
            storage_location_id = None
            storage = stock.retrieve_storage_locations({"storage_location_name":self.case_data['数据'][0]['库存地点']})
            for i in range(len(storage.json()['content'])):
                item = storage.json()['content'][i]
                if(item['storage_location_name'] == self.case_data['数据'][0]['库存地点']):
                    storage_location_id = item['id']
            param = {
                'material_id':material_id,
                'storage_location_id':storage_location_id
            } 
            r = stock.retrieve(param)
            assert (r.status_code == 200)
            total_elements=r.json()["total_elements"]
            #传入筛选条件给导出库位库存明细导出接口
            # 此处查询条件为：测试数据中所给的库存地点和物料
            #param["sort"]=["materialNo,descending"]
            #param["material_no"]=material_no
            r=bc_task.export_total_stock(param)
            assert r.status_code ==200
            #查询任务中心新建的到货单导出任务->查询成功->校验
            r=task.retrieve({"size": 20,"page": 0})
            assert r.status_code ==200
            #根据已有的任务列表，找到刚刚创建的导出任务
            #最简单的方式，按照导出任务的第一个"库位库存查询明细明细导出"任务
            id=""
            for items in r.json()["content"]:
                if items["name"] == "库存汇总导出":
                    id=id+items["id"]
                    break
            #比较接近实际的方式，根据时间比较判断
            #任务成功->获取导出文件地址exportFileUrl->校验
            status="CREATED"
            print(id)
            while status == "CREATED":
                time.sleep(5)#考虑到可能查询时候任务未完成，设置5秒一查
                r=task.retrieve({"size": 20,"page": 0})
                for items in r.json()["content"]:
                    if items["id"]==id:
                        if items["status"]=="CREATED":
                            break
                        elif items["status"]=="EXECUTING":
                            break
                        elif items["status"]=="SUCCEEDED":
                            status="SUCCEEDED"
                            exportFileUrl=items["extra"]["exportFileUrl"]   
                            break
                        else:
                            Logger.info("任务创建失败")
                            pytest.fail()
            #下载导出文件，并与库位库存查询明细总数对比
            task.check_export_task(exportFileUrl,"库存汇总导出.csv",total_elements)
            
    class Submit_warehousing_with_gifts(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/其他入库/511-赠品入库', text)
        @allure.step
        def run(self):
            warehousing_by_other_ways_with_so(self.case_data["数据"],'SHIPPED SO')

    class Production_stock_with_mo_warehouse_application(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/生产入库/参考工单入库申请单', text)
        @allure.step
        def run(self):
            #实际步骤：选择参考单据类型为”工单入库申请单"，选择参考的单据（已废弃的无法参考），选择库存类型，仓库，库存地点，移动原因，数量，然后提交。校验
            #此处根据测试数据循环新创建工单，再根据这个工单入库申请单，再进行入库
            wo_id_list=[]
            for workinfo in self.case_data["数据"][0]["工单创建需要数据"]:    
                wo_id=create_and_finish_workorder(workinfo["工单"][0]["创建信息"],workinfo["工单"][1]["完工日期"][0])
                wo_id_list.append(wo_id)
            mo_id=create_mo_warehouse_application(wo_id_list)
            #入库

            #获取工厂名，工厂id
            r=goods_movement.get_plant_info({})
            self.response_info(r)
            plant_id=r.json()[0]["id"]#此处先默认选择第一个
            plant_name=r.json()[0]["plant_name"]

            #获取移动方式的id、no、desc等
            r=warehouse.get_move_types({"move_type_no": "131"})
            self.response_info(r)
            move_type_id=r.json()[0]["move_type_id"]
            move_type_no=r.json()[0]["move_type_no"]
            move_type_desc=r.json()[0]["description1"]
            order_mode=""
            move_type_config_id=""
            ref_type=""
            for config in r.json()[0]["configs"]:
                if config["order_name"]=="工单入库申请单":
                    order_mode=order_mode+config["mode"]
                    move_type_config_id=move_type_config_id+config["id"]
                    ref_type=ref_type+config["order_type"]


            #获取仓库的id、no、name
            r=warehouse.get_warehouse_no({"exclude_forbidden_in":True})
            self.response_info(r)
            if len(r.json())==0:
                Logger.info("无仓库信息")
                pytest.fail()
            warehouse_id=""
            warehouse_no=""
            warehouse_name=""
            storage_location_id=""
            storage_location_name=""
            for wh in r.json():
                if "storage_locations" in wh:
                    warehouse_id=warehouse_id+wh["id"]
                    warehouse_no=warehouse_no+wh["warehouse_no"]
                    warehouse_name=warehouse_name+wh["warehouse_no_name"]
                    storage_location_id=storage_location_id+wh["storage_locations"][0]["id"]
                    storage_location_name=storage_location_name+wh["storage_locations"][0]["storage_location_name"]
                    break
            if storage_location_id == "":
                Logger.info("无库存地点信息")
                pytest.fail()
            
            #选取仓库库位
            query_bins={
                    'warehouse_no':warehouse_no,
                    'page':0,
                    'size':9999
                }
            r=warehouse.retrieve(data=query_bins,unique_instruction='retrieve_bins')
            self.response_info(r)
            bin_id=r.json()["content"][0]["bin_id"]
            bin_no=r.json()["content"][0]["bin_no"]


            #获取参考单据数据
            ref_id=mo_id
            r=mo_warehouse_application.get_detail({"mo_warehouse_application_id":ref_id})
            self.response_info(r)
            ref_no=r.json()["order_no"]
            items=r.json()["mo_warehouse_application_item_list"]
            sequence=1
            stock_type=self.case_data["数据"][1]["入库需要数据"][0]["库存类型"]
            for item in items:
                material={
                    "id":item["material_id"],
                    "material_no":item["material_no"]
                }
                goods_quantity=0
                judge=0
                for goods in self.case_data["数据"][1]["入库需要数据"][1]["入库物料"]:
                    if goods["交付物编号"] == item["material_no"]:
                        goods_quantity=goods["入库数量"]+goods_quantity
                        judge=1
                if judge==0:
                    Logger.error("测试数据中未给出物料"+item["material_no"]+"的入库数量")
                    pytest.fail()
                if item["open_quantity"]<goods_quantity:
                    Logger.error("入库数量大于可入库数量")
                    pytest.fail()
                item["material"]=material
                item["bin_id"]=bin_id
                item["quantity"]=goods_quantity
                item["sequence"]=sequence
                item["bin_no"]=bin_no
                #item["store_quantity"]=self.case_data["数据"][2]["入库需要数据"][0]["入库数量"]
                item["stock_type"]=stock_type
                item["ref_id"]=ref_id
                item["ref_no"]=ref_no
                item["ref_type"]=ref_type
                item["ref_item_id"]=item["id"]
                item["qty"]=goods_quantity
                item["auxiliary_quantity"]=goods_quantity
                item["destination_bin_id"]=bin_id
                item["destination_bin_no"]=bin_no
                item["destination_stock_type"]=stock_type
                
                item["ref_item_no"]=None
                item["po_no"]=None
                item["project_name"]=None
                item["so_no"]=None
                item["mfr_material_no"]=None
                item["brand"]=None
                item["unit_name"]=None
                item["supplier_id"]=None
                item["batch_no"]=None
                item["bin"]=None
                item["ref_remain_quantity"]=None
                item["storage_location_name"]=None
                item["has_child"]=False
                item["summary_quantity"]=None
                item["select"]=None
                item["delivery_completed"]=True
                item["move_type_desc"]=None
                item["move_type_id"]=None
                item["move_type_no"]=None
                item["ref_item_numc"]=None
                item["so_id"]=None
                item["lot_name"]=None
                item["field_values"]=None
                item["destination_special_stock"]=False
                item["destination_special_stock_type"]=None
                item["destination_special_stock_ref_type"]=None
                item["destination_special_stock_ref_id"]=None

                sequence=sequence+1

            #包装数据
            data={}
            data["plant_id"]=plant_id
            data["plant_name"]=plant_name
            data["move_type_id"]=move_type_id
            data["move_type_no"]=move_type_no
            data["move_type_desc"]=move_type_desc
            data["order_mode"]=order_mode
            data["move_type_config_id"]=move_type_config_id
            data["ref_type"]=ref_type
            data["ref_id"]=ref_id
            data["ref_no"]=ref_no
            data["warehouse_id"]=warehouse_id
            data["warehouse_no"]=warehouse_no
            data["warehouse_name"]=warehouse_name
            data["destination_warehouse_id"]=warehouse_id
            data["destination_warehouse_no"]=warehouse_no
            data["destination_warehouse_name"]=warehouse_name
            data["storage_location_id"]=storage_location_id
            data["storage_location_name"]=storage_location_name
            data["destination_storage_location_id"]=storage_location_id
            data["destination_storage_location_name"]=storage_location_name
            data["stock_type"]=stock_type
            data["move_reason_code"]="NA"
            data["move_reason_desc"]="正常操作"
            data["items"]=items

            data["remark"]=None
            data["used_unit"]=None
            data["source_warehouse_id"]=None
            data["source_warehouse_no"]=None
            data["source_warehouse_name"]=None
            data["doc_at"]=None
            data["source_storage_location_id"]=None
            data["source_storage_location_name"]=None
            data["is_hide_data"]=None
            data["request_by"]=None
            data["org_id"]=None
            data["float_entry"]=None

            r=goods_movement.create(data)
            self.response_info(r)
            #校验
            #校验内容为：入库的物料、入库的数量及其库存类型
            goods_movement_id=r.json()["id"]
            r=material_doc.get_detail({"material_doc_id":goods_movement_id})
            check_data_list=[]
            for item in r.json()["items"]:
                check_data={}
                check_data["交付物编号"]=item["material_no"]
                check_data["入库数量"]=item["qty"]
                check_data["库存类型"]=item["stock_type"]
                check_data_list.append(check_data)
            self.is_list_same(check_data_list,self.case_data["期望校验数据"])


    class Production_stock_with_work_order(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('仓库管理/生产入库/参考工单', text)
        @allure.step
        def run(self):
            #实际步骤：选择参考单据类型为"生产工单"，选择参考的单据，选择库存类型，仓库，库存地点，移动原因，数量，然后提交。校验
            #此处选择新创建一个工单，再进行入库
            wo_id_list=[]
            for workinfo in self.case_data["数据"][0]["工单创建需要数据"]:    
                mo_id=create_and_finish_workorder(workinfo["工单"][0]["创建信息"],workinfo["工单"][1]["完工日期"][0])
                wo_id_list.append(mo_id)
            #获取工厂名，工厂id
            r=goods_movement.get_plant_info({})
            self.response_info(r)
            plant_id=r.json()[0]["id"]#此处先默认选择第一个
            plant_name=r.json()[0]["plant_name"]

            #获取移动方式的id、no、desc等
            r=warehouse.get_move_types({"move_type_no": "131"})
            self.response_info(r)
            move_type_id=r.json()[0]["move_type_id"]
            move_type_no=r.json()[0]["move_type_no"]
            move_type_desc=r.json()[0]["description1"]
            order_mode=""
            move_type_config_id=""
            ref_type=""
            for config in r.json()[0]["configs"]:
                if config["order_name"]=="生产工单":
                    order_mode=order_mode+config["mode"]
                    move_type_config_id=move_type_config_id+config["id"]
                    ref_type=ref_type+config["order_type"]


            #获取仓库的id、no、name
            r=warehouse.get_warehouse_no({"exclude_forbidden_in":True})
            self.response_info(r)
            if len(r.json())==0:
                Logger.info("无仓库信息")
                pytest.fail()
            warehouse_id=""
            warehouse_no=""
            warehouse_name=""
            storage_location_id=""
            storage_location_name=""
            for wh in r.json():
                if "storage_locations" in wh:
                    warehouse_id=warehouse_id+wh["id"]
                    warehouse_no=warehouse_no+wh["warehouse_no"]
                    warehouse_name=warehouse_name+wh["warehouse_no_name"]
                    storage_location_id=storage_location_id+wh["storage_locations"][0]["id"]
                    storage_location_name=storage_location_name+wh["storage_locations"][0]["storage_location_name"]
                    break
            if storage_location_id == "":
                Logger.info("无库存地点信息")
                pytest.fail()
            
            #选取仓库库位
            query_bins={
                    'warehouse_no':warehouse_no,
                    'page':0,
                    'size':9999
                }
            r=warehouse.retrieve(data=query_bins,unique_instruction='retrieve_bins')
            self.response_info(r)
            bin_id=r.json()["content"][0]["bin_id"]
            bin_no=r.json()["content"][0]["bin_no"]

            
            #获取参考单据数据
            item_list=[]
            stock_type=self.case_data["数据"][1]["入库需要数据"][0]["库存类型"]

            for wo_id in wo_id_list:
                ref_id=wo_id
                r=work_order.get_detail({"production_plan_id":ref_id})
                self.response_info(r)
                sequence=1
                items={}
                items["sequence"]=sequence
                material={
                "id":r.json()["material"]["mdm_material_id"],
                "material_no":r.json()["material"]["material_no"]
                }
                goods_quantity=0
                judge=0
                for goods in self.case_data["数据"][1]["入库需要数据"][1]["入库物料"]:
                    if goods["交付物编号"] == r.json()["material"]["material_no"]:
                        goods_quantity=goods["入库数量"]+goods_quantity
                        judge=1
                if judge==0:
                    Logger.error("测试数据中未给出物料"+r.json()["material"]["material_no"]+"的入库数量")
                    pytest.fail()
                ret_data={}
                ret_data["mo_no"]=r.json()["sn"]
                #下发搜索信息
                ret_data["only_finished"]=True
                ret_data["ship_type"]="IN"
                ret_data["size"]=20
                ret_data["page"]=0
                rsep=material_pick.workorder_retrieve(ret_data)
                if rsep.json()['content'][0]["open_quantity"]<goods_quantity:
                    Logger.error("入库数量大于可入库数量")
                    pytest.fail()
                items["material"]=material
                items["material_id"]=r.json()["material"]["mdm_material_id"]
                items["material_name"]=r.json()["material"]["material_name"]
                items["material_group"]=r.json()["material"]["material_group"]
                items["material_no"]=r.json()["material"]["material_no"]
                items["material_desc"]=r.json()["material"]["material_desc"]
                items["planned_lead_time"]=r.json()["material"]["planned_lead_time"]
                items["material_unit"]=r.json()["material"]["material_unit"]

                items["bin_id"]=bin_id
                items["quantity"]=goods_quantity
                items["bin_no"]=bin_no
                items["id"]=r.json()["id"]
                items["mo_no"]=r.json()["sn"]
                items["total_quantity"]=r.json()["total_quantity"]
                items["completed_quantity"]=0
                items["shipped_qty"]=r.json()["shipped_qty"]
                items["open_quantity"]=r.json()["total_quantity"]
                items["finish_status"]=r.json()["finish_status"]
                items["pp_plan_prod_date"]=r.json()["plan_prod_date"]
                items["pp_plan_stock_date"]=r.json()["plan_stock_date"]
                items["pe_area_name"]=r.json()["pe_area_name"]
                items["material_unit_vo"]=r.json()["material"]["material_unit_vo"]
                items["order_no"]=r.json()["sn"]
                items["ref_no"]=r.json()["sn"]
                items["ref_id"]=r.json()["id"]
                items["stock_type"]=stock_type

                items["ref_type"]=ref_type
                items["ref_item_id"]=items["id"]
                items["qty"]=goods_quantity
                items["auxiliary_quantity"]=goods_quantity
                items["destination_bin_id"]=bin_id
                items["destination_bin_no"]=bin_no
                items["destination_stock_type"]=stock_type
                
                items["ref_item_no"]=None
                items["po_no"]=None
                items["project_name"]=None
                items["so_no"]=None
                items["mfr_material_no"]=None
                items["brand"]=None
                items["unit_name"]=None
                items["supplier_id"]=None
                items["supplier"]=None

                items["batch_no"]=None
                items["bin"]=None
                items["ref_remain_quantity"]=None
                items["storage_location_name"]=None
                items["has_child"]=False
                items["summary_quantity"]=None
                items["select"]=False
                items["issued"]=False

                items["contract_name"]=None

                items["move_type_desc"]=None
                items["move_type_id"]=None
                items["move_type_no"]=None
                items["ref_item_numc"]=None
                items["so_id"]=None
                items["lot_name"]=None
                items["field_values"]=None
                items["destination_special_stock"]=False
                items["destination_special_stock_type"]=None
                items["destination_special_stock_ref_type"]=None
                items["destination_special_stock_ref_id"]=None
                
                item_list.append(items)
            #包装数据
            data={}
            data["plant_id"]=plant_id
            data["plant_name"]=plant_name
            data["move_type_id"]=move_type_id
            data["move_type_no"]=move_type_no
            data["move_type_desc"]=move_type_desc
            data["order_mode"]=order_mode
            data["move_type_config_id"]=move_type_config_id
            data["ref_type"]=ref_type
            data["ref_id"]=None
            data["ref_no"]=None
            data["warehouse_id"]=warehouse_id
            data["warehouse_no"]=warehouse_no
            data["warehouse_name"]=warehouse_name
            data["destination_warehouse_id"]=warehouse_id
            data["destination_warehouse_no"]=warehouse_no
            data["destination_warehouse_name"]=warehouse_name
            data["storage_location_id"]=storage_location_id
            data["storage_location_name"]=storage_location_name
            data["destination_storage_location_id"]=storage_location_id
            data["destination_storage_location_name"]=storage_location_name
            data["stock_type"]=stock_type
            data["move_reason_code"]="NA"
            data["move_reason_desc"]="正常操作"
            data["items"]=item_list

            data["remark"]=None
            data["used_unit"]=None
            data["source_warehouse_id"]=None
            data["source_warehouse_no"]=None
            data["source_warehouse_name"]=None
            data["doc_at"]=None
            data["source_storage_location_id"]=None
            data["source_storage_location_name"]=None
            data["is_hide_data"]=None
            data["request_by"]=None
            data["org_id"]=None
            data["float_entry"]=None
            data["mo_ids"]=wo_id_list


            r=goods_movement.create(data)
            self.response_info(r)
            #校验
            #校验内容为：入库的物料、入库的数量及其库存类型
            goods_movement_id=r.json()["id"]
            r=material_doc.get_detail({"material_doc_id":goods_movement_id})
            check_data_list=[]
            for item in r.json()["items"]:
                check_data={}
                check_data["交付物编号"]=item["material_no"]
                check_data["入库数量"]=item["qty"]
                check_data["库存类型"]=item["stock_type"]
                check_data_list.append(check_data)
            self.is_list_same(check_data_list,self.case_data["期望校验数据"])
            
manager=Manager()
