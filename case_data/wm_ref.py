
from abc import abstractclassmethod
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
from manager.abstract_case import convert_data

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
from manager.abstract_case import Abstract_case
from interface.md.mdm_material import material
from interface.pe.area import area
from interface.pe.route import route
from interface.wm.mo import mo
from interface.wm.mo_warehouse_application import mo_warehouse_application


#创建有bom物料的MO，并将该MO置为已释放状态
def Create_work_order(data_list):
    bom_material_id = material.get_field_by_name(data=data_list[2], filed_name='id')
    product_material_id = material.get_field_by_name(data=data_list[0], filed_name='id')
    
    bom_qty = data_list[2]['数量']
    pruduct_qty = data_list[0]['数量']
    pe_area_name = data_list[1]['区域']
    pe_route_name = data_list[1]['工艺路线']
    plan_prod_date = data_list[1]['计划上线日期']
    plan_stock_date = data_list[1]['计划完成日期']
    
    picking_storage_location_name = data_list[1]['自制发货库存地点']
    picking_stock_location = stock.retrieve_storage_locations({"storage_location_name":picking_storage_location_name})
    picking_storage_location_id = picking_stock_location.json()['content'][0]['id']
    
    area =  produce_manage.get_area({"area_name_like":pe_area_name})
    route = produce_manage.get_route({"route_name":pe_route_name})
    area_id= area.json()['content'][0]['id']
    route_id = route.json()['content'][0]['id']
    body ={
    "reference_document_type": "HAND_TIED_SO",      #手绑销售订单(不关联SO)
    "kitting_items": [
        {
            "md_material_id": bom_material_id,
            "material_id": bom_material_id,
            "bom_qty": bom_qty,
            "picking_storage_location_id":picking_storage_location_id,
            "location": True,
            "sequence": 0,
            #"children": [],
            "leaf": True,
            #"level": 1,
            "expanded": True,
            "last_child": [True],
        }
    ],
    
    "material_id": product_material_id,     #产品id
    "mo_type": "PRODUCTION_ORDER",           #类型：生产工单
    #"pe_route_id": "20001",
    "pe_route_id": area_id,
    #"pe_area_id": "20001",
    "pe_area_id": route_id,
    #"plan_prod_date": "2021-09-14T00:00:00",
    "plan_prod_date": plan_prod_date,
    #"plan_stock_date": "2021-09-16T00:00:00",
    "plan_stock_date": plan_stock_date,
    #"total_quantity": "10",
    "total_quantity": pruduct_qty,
    "matching_bom": False,
    #"pe_area_name": "默认车间",
    "pe_area_name": pe_area_name,
    #"pe_route_name": "默认工序",
    "pe_route_name": pe_route_name,
    #"completed_quantity": 0,              #产品已完成数量
    "kitting_status": 10
        }
    #创建MO
    mo = work_order.create(body)  # response: {"id" : "6f4a0203b9014153ba30144dccd33bc5"}
    assert(mo.status_code == 200)
    mo_id = mo.json()['id']
    #释放MO
    work_order.release({"production_plan_id":mo_id})
    result = commons.dict_add({
        "mo_id":mo_id,
        "material_id":product_material_id
    })
    return result


#MO完工并入库
def MO_finish_and_into_stock(data_list):
    #创建MO
    mo = Create_work_order(data_list)
    mo_id = mo['mo_id']
    #点击完工设置生产进度(全量完工)
    data = [{
        "id":mo_id,
        "finish_mode":"FINISH_TOTALLY"
            }]

    work_order.finish_update(data)

    #完成工单
    # body = {
    #     "finish_date": "2021-09-23",    #实际完工日期
    #     "production_plans": [{"id": mo_id}]
    # }
    #在测试中发现不执行这一步也可
    #work_order.finish_process(body)

    #将已完工的MO执行生产入库
    #从完工的MO中获取mo_id和material_id
    material_id = mo['material_id']

    #若生产工单是关联销售订单
    mo_detail = work_order.get_detail({"production_plan_id": mo_id})
    #so_no = mo_detail.json()['document_no']
    #so = sales_order.retrieve({"so_query": so_no})
    #so_id = so.json()['content'][0]['id']
    #每次生产入库1,便于测试
    qty = data_list[4]['数量']
    item = commons.dict_add({
        "material_id": material_id,
        "id": mo_id,
        #"ref_no": mo_no,
        "ref_id": mo_id,
        "ref_type": "MO",
        "ref_item_id": mo_id,
        "qty": qty,
        "destination_stock_type": "UU",
        "destination_special_stock": False,
        #"destination_special_stock_type": "Q",
        #"destination_special_stock_ref_type": "SO",
        #"destination_special_stock_ref_id": so_id
    }, get_bin_info_4_warehouse_movement(data_list[3]))
    body = commons.dict_add({
        "move_type_id": "b9d64f3e2d4011ea978d00505634f437",
        "move_type_no": "131",
        "move_type_desc": "131-生产工单入库",
        "ref_type": "MO",
        "stock_type": "UU",
        "order_mode": "RHM",
        "move_reason_code": "NA",
        "move_reason_desc": "正常操作",
        "items": [item]
    }, get_plant_info(), get_warehouse_info_4_warehouse_movement(data_list[3]))

    r = goods_movement.create(body)
    assert(len(r.json()['id']) > 0)
    doc_id = r.json()['id']

    # 校验物料凭证存在
    material_doc_info = material_doc.get_detail({'material_doc_id': doc_id})
    assert(r.status_code == 200)
    assert(dict(material_doc_info.json()).__contains__('material_doc'))
    
    return mo


# 判断租户下有没有某个移动类型
'''
@Parameter move_type_no 业务类型编号，例如701
@Parameter order_type   goods-movements 请求参数中的ref_type参数，即参考单号类型，例如PO，SO，SASO等等
'''
def check_move_type_exists(move_type_no: str,order_type: str=None):
    move_type_list = None
    if 'wm' in global_data.data:
        if 'move_type_list' in global_data.data['wm']:
            move_type_list = global_data.data['wm']['move_type_list']
        else:
            move_type_list = warehouse.get_all_move_types().json()
            global_data.data['wm']['move_type_list'] = move_type_list
    else:
         move_type_list = warehouse.get_all_move_types().json()
         global_data.data['wm'] = {'move_type_list':move_type_list}

    for move_type in move_type_list:
        if move_type['move_type_no'] == move_type_no:
            configs = move_type['configs']
            for config in configs:
                if config['order_type'] == order_type:
                    return
    pytest.skip()

# 初始化时，查询仓库模块依赖的AO，PO，MO，SO用例
def query_related_orders(order_type : str) -> dict:
    order_dict = {}
    # 如果已经存在于global_data.data中直接取
    if global_data.data.__contains__('wm') :
        if dict(global_data.data["wm"]).__contains__(order_type):
            return global_data.data['wm'][order_type]
        else:
            # global_data.data['wm'] 存在，global_data.data['wm'][order_type]不存在
            order_dict = create_orders_by_order_type(order_type)
            # 塞global_data.data['wm'][order_type]
            global_data.data['wm'][order_type] = order_dict
            return order_dict        
    else: 
        # global_data.data['wm'] 不存在，塞global_data.data['wm']
        order_dict = create_orders_by_order_type(order_type)
        global_data.data['wm'] = {order_type:order_dict}
        return order_dict

# 根据订单类型创建相应的订单

def create_orders_by_order_type(order_type : str) -> dict:
    '''
    order_type:
    RETURN SRSO=>退货SO
    COMMON SO=>普通SO
    SHIPPED SO=>已发货的SO

    '''
    data_list = []
    # 新建相应的参考订单
    if (order_type.upper() == 'RETURN SRSO') : # 退货SO updated passed
        # 创建退货SO用例:
        so_id = create_so(data_list,1,True)
        # 下发 captain 租户不需要审批
        sales_order.create_approval({'so_id':so_id,'task_config':None})
        return sales_order.get_detail({'so_id':so_id}).json()
    elif (order_type.upper() == 'COMMON SO'): # 普通SO updated passed
        # 创建普通SO用例，无需下发
        so_id = create_so(data_list)
        return sales_order.get_detail({'so_id':so_id}).json()
    elif (order_type.upper() == 'SHIPPED SO'): # 已发货的SO updated passed
        # 创建SO用例：
        so_id = create_so(data_list)
        # 下发
        sales_order.create_approval({'so_id':so_id,'task_config':None})
        return sales_order.get_detail({'so_id':so_id}).json()
    elif (order_type.upper() == 'RETURNED PO'): # 审批的PO updated PASSED
        new_po_id = create_po_and_submit('R')
        return purchase_order.get_detail({'po_id':new_po_id}).json()
    elif (order_type.upper() == 'SHIPPED PO'): # 采购入库关联的PO #TODO TO BE CHECKED
        new_po_id = create_po_and_submit('N')
        return purchase_order.get_detail({'po_id':new_po_id}).json()
    elif (order_type == 'OUTSOURCING PO') :
        new_po_id = create_po_and_submit('N','委外加工采购')
        return purchase_order.get_detail({'po_id':new_po_id}).json()
    elif (order_type.upper() == 'COMMON TO'): # update #TODO retrieve by multiple conditions or create one TO
        if global_data.data.__contains__('wm'):
            material_doc_id = global_data.data["wm"]["material_doc_id"]
            return material_doc.get_detail({'material_doc_id':material_doc_id}).json()
        else:
            return material_doc.get_detail({'material_doc_id':'3d8ff7a6ea8c431ba2bcfa2998d65f90'}).json()
    elif (order_type.upper() == 'REF203 TO'): 
        # 查询一个203 出库单据
        to = material_doc.retrieve_tos({
            'move_type_code':'203',
            'source_warehouse_no':'01'
        }).json()['content'][0]
        to_id = to['id']
        to_detail = material_doc.get_tos_detal({'id':to_id}).json()
        return to_detail
    elif (order_type == 'COMMON SASO'): # updated passed
        # AUTO_wm1 
        so_id = create_so(data_list,has_products = True)
        sales_order.create_approval({'so_id':so_id,'task_config':None})
        return sales_order.get_detail({'so_id':so_id}).json()
    elif (order_type == 'SHIPPED SOSA'): # updated passed
        sosa_id = create_so(data_list,has_products = True)
        sales_order.create_approval({'so_id':sosa_id,'task_config':None})
        sosa_detail = sales_order.get_detail({'so_id':sosa_id}).json()
        so_shipment_lines=[]
        so_ids=[]
        for product in sosa_detail['products']:
            so_shipment_lines.append({
                "so_id": product['so_id'],
                'material_id':product['material_id'],
                'total_qty':1,
                'so_item_id':product['id']
            })
            so_ids.append(
                product['so_id']
            )
        so_shipments = sales_order_shipments.create({
            'so_shipment_lines':so_shipment_lines,
            "receipt_save_address": {
                "country": "100000",
                "province": "320000",
                "city": "320500",
                "district": "320505",
                "address_detail": "苏悦湾",
                "full_address": "中国江苏省苏州市虎丘区苏悦湾"
            },
            "shipment_save_address": {
                "country": "100000",
                "province": "320000",
                "city": "320500",
                "district": "320506",
                "address_detail": "星湖街",
                "full_address": "中国江苏省苏州市吴中区星湖街"
            },
            "so_ids": so_ids
        })
        return sales_order_shipments.get_detail({'sales_order_shipment_id':so_shipments.json()['id']}).json()

    else :
        # key err
        Logger.error('key error!!!')
        pytest.fail()

def create_so(data_list: list, order_type: int=0,has_products:bool=False) -> str:
    time_stamp = 'wm_'+str(int(time.time()))#防止时间戳和其他模块混合，而且不能影响其他模块的模糊查询只能这么改！！！
    if data_list == None:
        data_list = []
    data_list.append({"q": "常钰"})
    data_list.append(convert_data({
                                    "统一信用代码": "AUTO_"+time_stamp, 
                                    "客户代码":"AUTO_沪上电气"+time_stamp,
                                    "客户简称": "AUTO_沪上电气"+time_stamp, 
                                    "客户名称": "AUTO_沪上电气"+time_stamp,
                                    "结算币种": "美元"
                                    } ))
    so_param = convert_data({
                            "销售订单名称": "AUTO_变电器销售"+time_stamp, 
                            "订单类型": order_type, 
                            "销售订单类型": "普通销售", 
                            "销售订单交期": "2021-09-25", 
                            "下单日期": "2021-09-06T10:52:25",
                            "原币币种": "美元", 
                            "重要程度": False, 
                            "币种汇率": 6, 
                            "业务员": "常钰"
                             })
    # 如果有交付信息，则需要多传入products参数
    if has_products:
        so_param = commons.dict_add(so_param,
        {   
            'products':[{
                "unit_price": "100.000000",
                "tax_rate": "13.00",
                "unit_tax_price": "113.000000",
                "total_tax_price": "1130.00",
                "quantity": "10",
                "material_id": material.get_field_by_name({'物料名称':'AUTO_mm1'},'id'),
                "required_delivery_date": "2021-09-23",
                "price_mode": "UNIT_TAX_PRICE",
                "total_price": "1000.00"
            }]
        }
        )
    Logger.info(so_param)
    data_list.append(so_param)
    # 获取下单者的id
    ordered_id = account.get_field_by_name(data_list[0],"id")
    new_customer = customer.create(data_list[1])
    customer_id = new_customer.json()['id']
    data_list[2]["orderedBy"] = ordered_id
    data_list[2]["account_id"] = customer_id
    # 调用sd接口新建一条so
    so = sales_order.create(data_list[2])
    # 获取so详情
    so_id = so.json()['new_id']
    return so_id

# 创建采购订单并且提交
def create_po_and_submit(order_type:str='N',purchase_tyep:str="原材料采购") -> str:
    # 创建PO的用例数据
    data_list=[
            {"本币币种":"美元","原币币种":"人民币","下单类型":order_type,"汇率":"6","采购类型":purchase_tyep},
            {"unit_price": "200.000000","tax_rate": "13.00","unit_tax_price": "226.000000","total_price": "400.00","total_tax_price": "452.00","required_delivery_date": "2021-08-31","purchase_qty": "10"},
            {"物料名称": "AUTO_mm_with_supplier"},{"供应商名称":"AUTO_mm"}
        ]
    material_list = material.retrieve(data_list[2])
    assert (material_list.status_code == 200)
    assert (len(material_list.json()['content']) > 0)

    material_id = material_list.json()['content'][0]['id']
    order_unit = material_list.json()['content'][0]['material_purchase_unit']
    po_item={
        'manual':True,
        "unit_price": data_list[1]['unit_price'],
		"tax_rate": data_list[1]['tax_rate'],
		"unit_tax_price": data_list[1]['unit_tax_price'],
	    "required_delivery_date": data_list[1]['required_delivery_date'],
        "purchase_qty": data_list[1]['purchase_qty'],
		"material_id": material_id,
		"order_unit": order_unit,
		# 自定义字段爱好
	    "field_values": 
        [
            # {
            # 'field_no': "ED2021072300007", 
            # 'field_value': "打球", 
            # 'biz_type': "SPM_PO_ITEM"
		    # }
        ]
        }
    # 供应商
    supplier_info = supplier.retrieve(data_list[3])
    assert(supplier_info.json()[0]['id'])

    supplier_id = supplier_info.json()[0]['id']
    # 请求body
    body=commons.dict_add({
        'ordered_by':account.get_field_by_name({"q": "常钰"},"id"),
        'ordered_date':'2021-08-24T17:24:27',
	    "supplier_id": supplier_id,
        'po_items':[po_item]
    },data_list[0]) 

    r = purchase_order.create_and_submit(body)
    assert (r.status_code == 200)

    # 将创建出来的PO放到global_data
    po_id = r.json()['new_id']
    return po_id

def convert_stock_num(original_num:int,rounding_decimal,numerator,denominator,stock2order:bool):#用于转换数据  rouning decimal取自哪个vo要看stock2order的真假
    '''
    original_num:库存操作数量转换前的原始int，可以是单据数量也可以是仓库数量
    '''
    stock_2_order_rate=int(numerator)/int(denominator)
    result= original_num * stock_2_order_rate if stock2order else original_num / stock_2_order_rate 
    return float(Decimal(result).quantize(Decimal(f"{10**(-rounding_decimal)}"), rounding = "ROUND_HALF_UP"))

def aprox_equal(num1,num2):#约等于,供存在精度问题时的判相等
    if abs(num1-num2)<0.0000000001:
        return True
    else:
        Logger.warning(f'近似比对中，参数不等，num1:{str(num1)},num2:{str(num2)}')
        return False

def strict_check(check_data,source_data):#checkdata={jsonpath:[value]},
    
    for key,value in check_data.items():
        tmp=jsonpath(source_data,key)
        if not tmp:
            Logger.error(f'严格校验中jsonpath{key}，未找到数据 ')
            assert False
        if not value==tmp:
            Logger.error(f'严格校验中jsonpath{key}，得到的结果{tmp}与预期{value}不符 ')
            assert False

from interface.wm.material_pick import material_pick

from interface.mm.purchase_order import purchase_order
from interface.mm.supplier import supplier

#其他出库/601-销售发运出库 方法
def out_warehouse_sale_with_so(data_list : list):

    so = sales_order.retrieve(data_list[0])
    so_id = so.json()['content'][0]['id']
    so_detail = sales_order.get_detail({'so_id':so_id})

    ref_id = so_detail.json()['id']
    ref_no = so_detail.json()['batch_no']
    ref_type = 'SO' # 关联SO

    item = commons.dict_add({
        'material_id': material.get_field_by_name(data=data_list[2],filed_name='id'),
        "qty":data_list[2]['数量'], 
        "source_stock_type": "UU", 
        "source_special_stock":True,
        "source_special_stock_type":"Q",
        "source_special_stock_ref_type":ref_type,
        "source_special_stock_ref_id":ref_id
    },get_source_bin_info_4_warehouse_movement(data_list[1]))
    body = commons.dict_add({
            "ref_no":ref_no,
            "ref_id":ref_id,
            "ref_type":ref_type,
            "move_reason_code":"NA", 
            "move_reason_desc":"正常操作", 
            "items":[item]
    },get_plant_info(),get_source_warehouse_info_4_warehouse_movement(data_list[1]),get_move_type(data_list[2]))
    r = goods_movement.create(body)
    assert(len(r.json()['id']) > 0)
    doc_id = r.json()['id']
    # 校验物料凭证存在 
    material_doc_info = material_doc.get_detail({'material_doc_id':doc_id})
    assert(r.status_code == 200)
    assert(dict(material_doc_info.json()).__contains__('material_doc'))

#获取源仓库库位的方法
def get_source_bin_info_4_warehouse_movement(data : dict) -> dict:
    bin_info = warehouse.get_warehouse_bin_info(data)
    return {
        'source_bin_id' : bin_info.json()['content'][0]['id'],
        'source_bin_no': bin_info.json()['content'][0]['storage_bin_no']
    }
#获取源仓库信息及库存地点信息
def get_source_warehouse_info_4_warehouse_movement(data : dict) -> dict:
    warehouse_info = warehouse.get_warehouse_no(data)
    return {
        'source_warehouse_id': warehouse_info.json()[0]['id'],
        'source_warehouse_no': warehouse_info.json()[0]['warehouse_no'],
        'source_warehouse_name': warehouse_info.json()[0]['warehouse_no_name'],
        'source_storage_location_id': warehouse_info.json()[0]['storage_locations'][0]['id'],
        'source_storage_location_name': warehouse_info.json()[0]['storage_locations'][0]['storage_location_name']
    }
'''
wm里面创建的po、SO等数据，和global_data中pu、sd的模块测试区分开来，存在wm这部分
'''

def create_pick_list_by_none(data_list:list,delivery_order_name:str='OPKLI'):
    # 校验新增了一条领料单
    query_pick_list_param = {
        'order_type':delivery_order_name,
        'status':'O'
    }
    # 查询新建之前的数量
    pick_list = material_pick.retrieve_pick_list(query_pick_list_param)
    qty_b4 = pick_list.json()['total_elements']
    Logger.info('qty_b4:'+str(qty_b4))

    mo_item_vo = {
            'material_id':material.get_field_by_name(data_list[1],'id'),
            'total_quantity':data_list[1]['领料数量']
        }
    body = commons.dict_add({
            'delivery_order_name':delivery_order_name,
            'mo_item_create_vos':[mo_item_vo],
            'requisition_type':'BY_NONE'
    },data_list[0])    
    new_po = material_pick.create(body).json()
    assert(len(new_po[0]['id']) > 0)

    # 新建后的领料单数量
    pick_list = material_pick.retrieve_pick_list(query_pick_list_param)
    qty_af = pick_list.json()['total_elements']
    aprox_equal(qty_af,qty_b4+int(data_list[1]['领料数量']))
    return new_po

def create_pick_list_ref_so(data_list:list,delivery_order_name:str='OPKLI',ref_so:str='SHIPPED SO'):
    order_detail = query_related_orders(ref_so)
    # 校验新增了一条领料单
    query_pick_list_param = {
        'order_type':delivery_order_name,
        'status':'O'
    }
    # 查询新建之前的数量
    pick_list = material_pick.retrieve_pick_list(query_pick_list_param)
    qty_b4 = pick_list.json()['total_elements']
    Logger.info('qty_b4:'+str(qty_b4))

    mo_item_vo = {
            'material_id':material.get_field_by_name(data_list[1],'id'),
            'total_quantity':data_list[1]['领料数量'],

        }
    body = commons.dict_add({
            'delivery_order_name':delivery_order_name,
            'mo_item_create_vos':[mo_item_vo],
            'requisition_type':'BY_SO',
            "document_id": order_detail['id'],
            "document_no": order_detail['batch_no'],
            "document_type": "SO"
    },data_list[0])    
    new_po = material_pick.create(body).json()
    assert(len(new_po[0]['id']) > 0)

    # 新建后的领料单数量
    pick_list = material_pick.retrieve_pick_list(query_pick_list_param)
    qty_af = pick_list.json()['total_elements']
    aprox_equal(qty_af,qty_b4+int(data_list[1]['领料数量']))
# 通用的获取plant_id，plant_name的方法
def get_plant_info() -> dict:
    r = goods_movement.get_plant_info({})
    return {
        'plant_id':r.json()[0]['id'],
        'plant_name':r.json()[0]['plant_name']
    }

# 通用的获取仓库信息以及库存地点的方法
def get_warehouse_info_4_warehouse_movement(data : dict) -> dict:
    warehouse_info = warehouse.get_warehouse_no(data)
    return {
        'destination_warehouse_id' : warehouse_info.json()[0]['id'],
        'destination_warehouse_no': warehouse_info.json()[0]['warehouse_no'],
        'destination_warehouse_name': warehouse_info.json()[0]['warehouse_no_name'],
        'destination_storage_location_id' : warehouse_info.json()[0]['storage_locations'][0]['id'],
        'destination_storage_location_name' : warehouse_info.json()[0]['storage_locations'][0]['storage_location_name']
    }
# 通用的获取仓库库位的方法
def get_bin_info_4_warehouse_movement(data : dict) -> dict:
    bin_info = warehouse.get_warehouse_bin_info(data)
    return {
        'destination_bin_id' : bin_info.json()['content'][0]['id'],
        'destination_bin_no': bin_info.json()['content'][0]['storage_bin_no']
    }

#通用的特殊库存处理办法
def get_special_stock_info(so_id):#目前只处理so的特殊库存
    if not so_id:
        return  {"destination_special_stock":False}
    else:
        so_no=sales_order.get_detail({'so_id':so_id}).json()['batch_no']
        return {
        "destination_so_id":so_id,
        "destination_so_no":so_no,
        "destination_special_stock":True,#必填相关
        "destination_special_stock_type":"Q",#FIXME
        "destination_special_stock_ref_type":"SO",
        "destination_special_stock_ref_id":so_id
        }

# 通用的获取move_types的方法
def get_move_type(data : dict) -> dict:
    move_type_list = global_data.data['wm']['move_type_list']
    for move_type_vo in move_type_list:
        if int(move_type_vo['move_type_no']) == int(data['移动类型编号']):
            return {
                'move_type_id': move_type_vo['move_type_id'],
                'move_type_no': move_type_vo['move_type_no'],
                'move_type_desc': move_type_vo['description1']
            }
    return {}


#  其他入库(关联SO)的通用方法
'''
参考用例数据：
[{"q": "常钰"},
{"统一信用代码": "AUTO_{start_timestamp}", "客户简称": "AUTO_沪上电气{start_timestamp}", "客户名称": "AUTO_沪上电气{start_timestamp}", "结算币种": "美元"},
{"销售订单名称": "AUTO_变电器销售{start_timestamp}", "订单类型": 1, "销售订单类型": "普通销售", "销售订单交期": "2021-09-25", "下单日期": "2021-09-06T10:52:25", "原币币种": "美元", "重要程度": False, "币种汇率": 6, "业务员": "常钰"},
{"仓库名称":"外购件库","库位编号":"QTK","仓库编号":"01"},{"移动类型编号":"233","物料名称":"AUTO_mm1","数量":"2"}]

如果测试用例关联的是普通的SO ，则第二个人参数order_type 传入COMMON SO(或者不传，默认是COMMON SO)
如果测试用例关联的退货SO，则第二个人参数需要传RETURN SRSO
'''
def warehousing_by_other_ways_with_so(data_list : list, order_type: str='SHIPPED SO'):
    warehousing_by_other_ways_with_orders(data_list,order_type)
    
#  其他入库(不关联SO)的通用方法
'''
参考用例数据：
[{"仓库名称":"外购件库","库位编号":"QTK","仓库编号":"01"},{"移动类型编号":"901","物料名称":"AUTO_mm1","数量":"1"}]
'''
def warehousing_by_other_ways_without_so(data_list : list):
    # ref_type = 'SO' # 关联SO
    ref_type = ''
    check_move_type_exists(data_list[1]['移动类型编号'],ref_type)
    item = commons.dict_add({
        'material_id': material.get_field_by_name(data=data_list[1],filed_name='id'),
        "qty":data_list[1]['数量'], #测试用例填入
        "destination_stock_type":"UU",
        "destination_special_stock":False,
    },get_bin_info_4_warehouse_movement(data_list[0]))
    body = commons.dict_add({
        "ref_type":ref_type,
        "move_reason_code":"NA", 
        "move_reason_desc":"正常操作", 
        "items":[item]
    },get_plant_info(),get_warehouse_info_4_warehouse_movement(data_list[0]),get_move_type(data_list[1]))
    r = goods_movement.create(body)
    assert(len(r.json()['id']) > 0)
    doc_id = r.json()['id']
    # 校验物料凭证存在 
    material_doc_info = material_doc.get_detail({'material_doc_id':doc_id})
    assert(r.status_code == 200)
    assert(dict(material_doc_info.json()).__contains__('material_doc'))
    # 校验相应的库位多了物料

# 其他入库关联PO
def warehousing_by_other_ways_with_po(data_list : list, order_type: str='RETURNED PO'):
    warehousing_by_other_ways_with_orders(data_list,order_type)

# 其他入库->关联TO
def warehousing_by_other_ways_ref_to(data_list : list, order_type: str='REF203 TO'):
    warehousing_by_other_ways_with_orders(data_list,order_type)

# 其他入库关联orders的方法:
def warehousing_by_other_ways_with_orders(data_list : list, order_type: str):
    order_detail = query_related_orders(order_type)
    ref_type = order_type.split(' ')[1]
    ref_id = ''
    ref_no = ''
    ref_item_id = None
    check_move_type_exists(data_list[1]['移动类型编号'],ref_type)
    if ref_type.__contains__('SO'):
        ref_id = order_detail['id']
        ref_no = order_detail['batch_no']
        if ref_type == 'SRSO':
            ref_item_id = order_detail['products'][0]['id']
    elif ref_type == 'PO':
        ref_id = order_detail['id']
        ref_no = order_detail['po_no']
        if 'SHIPPED PO' == order_type:
            ref_item_id = order_detail['items'][0]['id']
    elif ref_type == 'TO':
        if order_type == 'COMMON TO':
            ref_id = order_detail['to_list'][0]['id']
            ref_no = order_detail['to_list'][0]['to_no']                #暂时写死  需要在261中创建出库单号
        if order_type == 'REF203 TO':
            ref_id = order_detail['id']
            ref_no = order_detail['to_no']
    
    # 入库api的请求体
    material_id = material.get_field_by_name(data=data_list[1],filed_name='id')
    destination_bin_info = get_bin_info_4_warehouse_movement(data_list[0])
    item = commons.dict_add({
        'material_id': material_id, # TODO 可以通过SO获取
        "qty":data_list[1]['数量'], # 测试用例填入
        "destination_stock_type":"UU", # code def
        "destination_special_stock": True if ref_type.__contains__('SO') else False,
        "destination_special_stock_type":"Q" if ref_type.__contains__('SO') else None,
        "destination_special_stock_ref_type":'SO' if ref_type.__contains__('SO') else None,
        "destination_special_stock_ref_id":ref_id if ref_type.__contains__('SO') else None,
        'ref_item_id':ref_item_id
    },destination_bin_info)
    destination_warehouse_info = get_warehouse_info_4_warehouse_movement(data_list[0])
    body = commons.dict_add({
            "ref_no":ref_no,
            "ref_id":ref_id,
            "ref_type":ref_type,
            "move_reason_code":"NA", 
            "move_reason_desc":"正常操作", 
            "items":[item]
    },get_plant_info(),destination_warehouse_info,get_move_type(data_list[1]))
    if 'SHIPPED PO' == order_type:
        body = commons.dict_add(body,{
            # 拓展自定义字段
            "field_values":[
                {"field_no":"ED2021090200043","field_value":1,"biz_type":"WM_TRANSORDER_HEAD"},
                {"field_no": "ED2021090200041","field_value": "2021-09-30","biz_type": "WM_TRANSORDER_HEAD"}
                ]
            })
    #查询库位现在的物料数量，以备校验
    query_bin_stock = {
        "warehouse_id":destination_warehouse_info['destination_warehouse_id'],
        'storage_bin_id':destination_bin_info['destination_bin_id'],
        'material_id':material_id,
        'empty_lot_name':True,
        'stock_type':'UU' #FIXME 做进codedef
    }
    stock_info_b4 = stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
    tmp_qty_list=jsonpath(stock_info_b4.json(),f'$.content[0].total_quantity')
    material_bin_qty_b4 = 0 if not tmp_qty_list else tmp_qty_list[0]
    Logger.info('material_bin_qty_b4:'+str(material_bin_qty_b4))

    r = goods_movement.create(body)
    assert(r.status_code == 200)
    assert(len(r.json()['id']) > 0)
    doc_id = r.json()['id']
    
    # 校验物料凭证存在且正确 
    material_doc_info = material_doc.get_detail({'material_doc_id':doc_id}).json()

    doc_no = material_doc_info['material_doc']['doc_no']
    #将生成的物料凭证no 放入global_data
    if global_data.data.__contains__("wm") :
        global_data.data['wm']['material_doc_no'] = doc_no
    else :
        global_data.data['wm']={"material_doc_no":doc_no}

    check_addition={
                    '$.items[0].material_id':[material_id],
                    '$.items[0].qty':[float(data_list[1]['数量'])],
                    "$.material_doc.ref_type" : [ref_type],
                    "$.material_doc.ref_id" : [ref_id],
                    '$.items[0].move_type_no':[data_list[1]['移动类型编号']],#FIXME
                    '$.items[0].stock_type':['UU'],
                    '$.items[0].move_reason_code':['NA'],
                    '$.items[0].storage_location_id':[destination_warehouse_info['destination_storage_location_id']],
                    '$.items[0].warehouse_id':[destination_warehouse_info['destination_warehouse_id']],
                    '$.items[0].storage_bin_id':[destination_bin_info['destination_bin_id']]
                    }
    strict_check(check_data=check_addition,source_data=material_doc_info)

    # 校验相应的库位多了物料 目前仓库库位查询那边有bug
    # stock_info_af = stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
    # material_bin_qty_af = jsonpath(stock_info_af.json(),f'$.content[0].total_quantity')[0] 
    # Logger.info('material_bin_qty_af:'+str(material_bin_qty_af))
    # assert aprox_equal(material_bin_qty_af,material_bin_qty_b4+check_addition['$.items[0].qty'][0]) 

# 其他出库关联orders的方法:
def oos_by_other_ways_with_orders(data_list: list, order_type: str) : 
    order_detail = query_related_orders(order_type)
    ref_type = order_type.split(' ')[1]
    Logger.info('移动类型编号:'+data_list[1]['移动类型编号'])
    check_move_type_exists(data_list[1]['移动类型编号'],ref_type)
    ref_id = ''
    ref_no = ''
    ref_item_id = ''
    if ref_type.__contains__('SO') and order_type != 'SHIPPED SOSA':
        ref_id = order_detail['id']
        ref_no = order_detail['batch_no']
        if ref_type == 'SRSO' or order_type == 'COMMON SASO':
            ref_item_id = order_detail['products'][0]['id']
        source_special_stock_ref_id = ref_id
    elif order_type == 'SHIPPED SOSA':
        ref_item_id = order_detail["so_shipment_lines" ][0]["id" ]
        ref_id = order_detail['id']
        ref_no = order_detail["shipment_no" ]
        source_special_stock_ref_id = order_detail['so_infos'][0]['so_id']
    elif ref_type == 'PO':
        ref_id = order_detail['id']
        ref_no = order_detail['po_no']
        source_special_stock_ref_id = ref_id

    bin_info = get_bin_info_4_warehouse_movement(data_list[0])
    warehouse_info = get_warehouse_info_4_warehouse_movement(data_list[0])
    material_id = material.get_field_by_name(data=data_list[1],filed_name='id')
    item = commons.dict_add({
        'material_id': material_id,
        "qty":data_list[1]['数量'], # 测试用例填入
        "source_stock_type":"UU", # code def
        "source_special_stock":True,
        "source_special_stock_type":"Q",
        "source_special_stock_ref_type":'SO' if ref_type.__contains__('SO') else ref_type,
        "source_special_stock_ref_id":source_special_stock_ref_id,
        'ref_item_id':ref_item_id
    },commons.dict_key_replace_key_word(bin_info,'destination','source'))
    body = commons.dict_add({
            "ref_no":ref_no,
            "ref_id":ref_id,
            "ref_type":ref_type,
            "move_reason_code":"NA", 
            "move_reason_desc":"正常操作", 
            "items":[item]
    },get_plant_info(),commons.dict_key_replace_key_word(warehouse_info,'destination','source'),get_move_type(data_list[1]))

    #查询库位现在的物料数量，以备校验
    query_bin_stock = {
        "warehouse_id":warehouse_info['destination_warehouse_id'],
        'storage_bin_id':bin_info['destination_bin_id'],
        'material_id': material_id,
        'empty_lot_name':True,
        'stock_type':'UU' #FIXME 做进codedef
    }
    stock_info_b4 = stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
    tmp_qty_list=jsonpath(stock_info_b4.json(),f'$.content[0].total_quantity')
    material_bin_qty_b4 = 0 if not tmp_qty_list else tmp_qty_list[0]
    Logger.info('material_bin_qty_b4:'+str(material_bin_qty_b4))

    r = goods_movement.create(body)
    assert(r.status_code == 200)
    assert(len(r.json()['id']) > 0)
    doc_id = r.json()['id']
    # 校验物料凭证存在且正确 
    material_doc_info = material_doc.get_detail({'material_doc_id':doc_id})
    check_addition={
                    '$.items[0].material_id':[material_id],
                    '$.items[0].qty':[float(data_list[1]['数量'])],
                    "$.material_doc.ref_type" : [ref_type],
                    "$.material_doc.ref_id" : [ref_id],
                    # '$.items[0].move_type_no':[data_list[1]['移动类型编号']],#FIXME
                    '$.items[0].stock_type':['UU'],
                    '$.items[0].move_reason_code':['NA'],
                    '$.items[0].storage_location_id':[warehouse_info['destination_storage_location_id']],
                    '$.items[0].warehouse_id':[warehouse_info['destination_warehouse_id']],
                    '$.items[0].storage_bin_id':[bin_info['destination_bin_id']]
                    }
    strict_check(check_data=check_addition,source_data=material_doc_info.json())

    # 校验相应的库位少了物料 目前仓库库位查询那边有bug
    # stock_info_af = stock.retrieve(data=query_bin_stock,unique_instruction='retrieve_bin_stock')
    # material_bin_qty_af = jsonpath(stock_info_af.json(),f'$.content[0].total_quantity')[0] 
    # Logger.info('material_bin_qty_af:'+str(material_bin_qty_af))
    # assert aprox_equal(material_bin_qty_af,material_bin_qty_b4+check_addition['$.items[0].qty'][0])
    return material_doc_info

# 其他出库的通用方法(关联SO):
'''
@Attention
这边的SO要注意两点：
1) 状态做到已下发
2) 项目料有库存
'''
def oos_by_other_ways_with_so(data_list : list,order_type: str='SHIPPED SO'):
    r = oos_by_other_ways_with_orders(data_list,order_type)  #这里新增返回值 material_doc_info
    return r

# 其它出库(关联PO)
def oos_by_other_ways_with_po(data_list : list,order_type: str='RETURNED PO'):
    oos_by_other_ways_with_orders(data_list,order_type)    


def create_and_finish_workorder(data,finish_data):
    #该创建工单的方法与第一个不同，该方法支持工单创建可配置化
    #关于物料的维护：选择每次自动创建，并去更新其BOM。            
    #根据计量单位组，查询主计量单位和采购单位，这两个单位都由unit_name得来
    
    r=material.material_unit_groups_page(data[1])
    assert r.status_code == 200
    material_unit_groups_id=r.json()['content'][0]['id']
    r=material.material_units_retrieve_by_measure_unit_groups({"id":material_unit_groups_id})
    assert r.status_code == 200

    if len(r.json())==0:
        Logger.error('未在系统准备必要的主计量单位')
        pytest.fail()
    material_units_name=r.json()[0]["unit"]["unit_name"]
    #循环创建所需要的物料
    for caseData in data:
        if "物料名称" in caseData:
            caseData["material_unit"]=material_units_name
            caseData["material_purchase_unit"]=material_units_name
            r=material.create(caseData)
            assert r.status_code == 200

    #修改物料的BOM
    BOM_info=material.get_bom_from_casedata(data[0]["BOM"])#获取物料BOM的关系
    #根据BOM去维护系统中物料的BOM的关系
    if len(BOM_info)!=0:
        for bom_info in BOM_info:
            material.update_bom(bom_info)
    
    #新建工单
    #内容包含 物料信息，子物料信息，其他信息
    r=material.retrieve({"material_no":data[2]["交付物"][0]["物料编号"]})
    material_id=r.json()["content"][0]["id"]
    material_name=r.json()["content"][0]["material_name"]
    material_no=r.json()["content"][0]["material_no"]
    #获取区域，id和名字
    r=area.retrieve_areas({"material_no":material_no})
    assert r.status_code == 200
    area_id=r.json()[0]["id"]
    area_name=r.json()[0]["area_name"]
    #获取工艺路线，id和名字
    r=route.retrieve_routes({"material_no":material_no})
    assert r.status_code == 200
    route_id=r.json()[0]["id"]
    route_name=r.json()[0]["route_name"]
    #获取主数据物料BOM树
    r=work_order.retrieve_bomm_tree([material_id])
    assert r.status_code == 200
    if "children" in r.json()[0]:#存在所添加的主数据没有子物料的情况，此处进行了处理。
        children_list=r.json()[0]["children"]
        material.recursiom_mixed_bom_data(children_list,1,0,None,[])
        kitting_status=0
            
    else:
        children_list=[]
        kitting_status=10
    #包装请求
    post_data={}
    post_data["reference_document_type"]="HAND_TIED_SO"
    post_data["contract_name"]=None
    post_data["contract_no"]=None
    post_data["account_name"]=None
    post_data["material_id"]=material_id
    post_data["material_name"]=material_name
    post_data["material"]={
                    "id":material_id,
                    "material_name":material_name,
                    "material_no":material_no
                }
    post_data["mo_type"]="PRODUCTION_ORDER"
    post_data["pe_route_id"]=route_id
    post_data["pe_area_id"]=area_id
    post_data["plan_prod_date"]=data[2]["交付物"][0]["计划上线时间"]
    post_data["plan_stock_date"]=data[2]["交付物"][0]["计划完成时间"]
    post_data["document_date"]=None
    post_data["document_id"]=None
    post_data["document_no"]=None
    post_data["document_name"]=None
    post_data["pe_route_name"]=route_name
    post_data["pe_area_name"]=area_name
    post_data["completed_quantity"]=0
    post_data["kitting_status"]=kitting_status
    post_data["kitting_items"]=children_list
    post_data["total_quantity"]=data[2]["交付物"][0]["数量"]
    r=work_order.create(post_data)
    assert r.status_code == 200
    work_order_id= r.json()["id"]
    
    #接着释放该工单
    r=work_order.release({"production_plan_id":work_order_id})
    assert r.status_code == 200

    #接着完工该工单
    #根据工单id批量获取工单详情
    wo_info=[]
    wo_info.append(work_order_id)
    r=work_order.get_detail_bulk_by_id(wo_info)
    assert r.status_code == 200
    #保存生产进度
    progress=[]
    progress_info={
                "id":work_order_id,
                "finish_mode":"FINISH_TOTALLY"
            }
    progress.append(progress_info)
    r=work_order.save_progress(progress)
    assert r.status_code == 200
    #判断是否该工单可以被完工
    r=work_order.finish_check(wo_info)
    assert r.status_code == 200
    if len(r.json()["exception_production_plans"])!=0:
        Logger.error('该工单无法被完工')
        pytest.fail()
    #执行完工
    finish_data["production_plans"]=[]
    del progress_info["finish_mode"]
    progress_info["exception_handles"]=None
    finish_data["production_plans"].append(progress_info)
    r=mo.finish_process(finish_data)
    assert r.status_code == 200
    return work_order_id

def create_mo_warehouse_application(work_order_id_list):
    #该方法根据传入的工单id，创建工单入库申请单，默认申请全部数量
    r=mo_warehouse_application.bulk({"mo_ids":work_order_id_list})
    assert r.status_code == 200
    mo_warehouse_application_item_create_list=[]
    for item in r.json():
        mo_warehouse_application_item_create={}
        mo_warehouse_application_item_create["mo_id"]=item["mo_id"]
        mo_warehouse_application_item_create["quantity"]=item["pending_delivery_quantity"]
        mo_warehouse_application_item_create["priority"]=None
        mo_warehouse_application_item_create["self_make_inbound_storage_location_id"]=None
        mo_warehouse_application_item_create["remark"]=None
        mo_warehouse_application_item_create_list.append(mo_warehouse_application_item_create)
    r=mo_warehouse_application.create({"mo_warehouse_application_item_create_list":mo_warehouse_application_item_create_list})
    assert r.status_code == 200
    mo_warehouse_application_id=r.json()["id"] 
    return mo_warehouse_application_id