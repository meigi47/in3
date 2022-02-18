
from utils.global_data import global_data
from interface.mm.price_record import price_record
from logging import Logger
from interface.wm.invoice import invoice
from interface.mm.contract import contract
from typing import *
import allure
from interface.mm.material import material
from manager.abstract_case import Abstract_case
import utils.commons as commons
from interface.mm.purchase_requirent import purchase_requirent
from interface.mm.purchase_order import purchase_order
from interface.mm.supplier import supplier
from interface.uaas.uaas import account
from utils.logger import Logger
from io import StringIO

from copy import deepcopy as dcp
from case_data.abstract_case_mgr import Abstrct_case_mgr


class Manager(Abstrct_case_mgr):
    def __init__(self) -> None:
        super().__init__()

    class case10(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购订单管理/查询', text)
        
        def run(self):
            r = purchase_order.retrieve(self.case_data['数据'][0])
            assert (r.status_code == 200)
            assert (len(r.json()['content']) >= self.case_data['期望校验数据'][0])

    class Edit_po_update(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购订单管理/编辑PO', text)

        def run(self):
            po_no = global_data.data["mm"]["po_manage"]["po_no"]
            # po_no = 'PO20210915000039'
            r = purchase_order.retrieve({"po_no":po_no})
        
            material_response = material.retrieve(self.case_data['数据'][2])
            material_id = material_response.json()['content'][0]['id']
            order_unit = material_response.json()['content'][0]['material_purchase_unit']

            assert (r.status_code == 200)
            # assert (len(r.json()['content'])  != 0)
            id = r.json()['content'][0]['id']
            exchange_rate = r.json()['content'][0]['exchange_rate']
            local_currency_no = r.json()['content'][0]['local_currency_no']
            order_type = r.json()['content'][0]['order_type']
            ordered_by = r.json()['content'][0]['ordered_by']
            supplier_id = r.json()['content'][0]['supplier_id']
            original_currency_no = r.json()['content'][0]['original_currency_no']
            required_delivery_date = r.json()['content'][0]['required_delivery_date']

            # purchase_type = self.case_data['数据'][0]["采购类型"]
            purchase_qty = self.case_data['数据'][1]["purchase_qty"]
            # open_qty =  self.case_data['数据'][1]["open_qty"]

            ordered_date =  self.case_data['数据'][1]['ordered_date']
            tax_rate = self.case_data['数据'][1]["tax_rate"]
            unit_price = self.case_data['数据'][1]["unit_price"]
            unit_tax_price = self.case_data['数据'][1]["unit_tax_price"]
            total_tax_price = self.case_data['数据'][1]["total_tax_price"]
            total_price = self.case_data['数据'][1]["total_price"]
            
            data={
                "po_id" : id,
                # "purchase_type:"190", 
                "local_currency_no":local_currency_no,
                "original_currency_no":original_currency_no,
                "exchange_rate":exchange_rate,
                "order_type":order_type,
                "ordered_date":ordered_date, #手填
                "po_items":[
                {
                "required_delivery_date":required_delivery_date,
                "purchase_qty":purchase_qty,
                # "open_qty":2,
                "tax_rate": tax_rate,
                # "tax":11.51,
                "unit_price":unit_price,
                "unit_tax_price":unit_tax_price,
                "total_tax_price":total_tax_price,
                "total_price":total_price,
                "exchange_rate":exchange_rate,
                "order_unit": order_unit,
                "material_unit":order_unit,
                "material_id":material_id,
                "field_values":[#FIXME
                    # {'field_no': "ED2021072300007", 
                    # 'field_value': "打球", 
                    # 'biz_type': "SPM_PO_ITEM"}
                    ],
                }
                ],
                "ordered_by":ordered_by,
                "supplier_id":supplier_id,
                "back_to_pr_flag":True
                }
                # )
            terminal_data = commons.dict_add(data,self.case_data["数据"][0])
            r = purchase_order.update(terminal_data)
            assert (r.status_code == 200)


    class Test_create_pr_ok_on_pr_list(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请列表/生成采购申请单', text)
        
        def run(self):
            material_list = material.retrieve(self.case_data['数据'][0])
            assert (material_list.status_code == 200)
            assert (len(material_list.json()['content']) > 0)

            id = material_list.json()['content'][0]['id']
            material_no = material_list.json()['content'][0]['material_no']
            order_unit = material_list.json()['content'][0]['material_purchase_unit']
            customer_id = account.get_field_by_name(self.case_data['数据'][3],"id")
            item = commons.dict_add({
                'field_values':[
                    {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300012','field_value':None},
                    {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300028','field_value':None},
                    {'field_no': "ED2021072300007", 'field_value': "打球", 'biz_type': "SPM_PR_ITEM"
                }
                ],
                'material_id':id,
                'material_no':material_no,
                'order_unit': order_unit
                },self.case_data['数据'][1])
                
            data = commons.dict_add({'items':[item]},{'ordered_by': customer_id})
            terminal_data = commons.dict_add(data,self.case_data['数据'][2])
            r1 = purchase_requirent.create_and_submit(terminal_data)
            assert (r1.status_code == 200)
            assert (len(r1.json()['new_id']) > 0)

            r2 = purchase_requirent.create_and_submit(terminal_data)
            assert (r2.status_code == 200)
            assert (len(r2.json()['new_id']) > 0)
            # 将采购订单管理中的id放到global_data里面（目前创建两条）
            prm_pr_list = []
            prm_pr_list.append({'pr_id':r1.json()['new_id']})
            prm_pr_list.append({'pr_id':r2.json()['new_id']})

            
            pr_manage = {'pr_manage':prm_pr_list,'customer_id':customer_id}
            global_data.data['mm'] = pr_manage

    # 采购申请列表 中复合查询采购申请单
    class Query_pr_ok_on_pr_list(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请列表/查询', text)
        
        def run(self):
            r = purchase_requirent.retrieve(self.case_data['数据'][0])
            assert (r.status_code == 200)
            assert (len(r.json()['content']) >= self.case_data['期望校验数据'][0])

    # 采购申请管理 中复合查询采购申请单
    class Query_pr_ok_on_prm(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请管理/查询', text)
        
        def run(self):
            r = purchase_requirent.retrieve_on_pr_manage(self.case_data['数据'][0])
            assert (r.status_code == 200)
            assert (len(r.json()['content']) >= self.case_data['期望校验数据'][0])

    # 采购管理/采购申请列表 编辑采购申请单
    class Edit_pr_ok__on_pr_list(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请列表/修改/编辑采购申请单', text)
        
        def run(self):
            material_name = self.case_data['数据'][0]['物料名称']
            pr_id = global_data.data['mm']['pr_list']['pr_id']
            # get pr by pr_id
            pr = purchase_requirent.get_detail({'pr_id':pr_id})
            assert(pr.status_code == 200)

            items = []
            for i in range(len(pr.json()['items'])):
                temp_item = pr.json()['items'][i]
                items.append({
                            'field_values':[
                                {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300012','field_value':None},
                                {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300028','field_value':None},
                                {'field_no': "ED2021072300007", 'field_value': "打球", 'biz_type': "SPM_PR_ITEM"}
                            ],
                            'id': temp_item['id'],
                            'material_id':temp_item['material']['material_id'],
                            'material_no':temp_item['material']['material_no'],
                            'material_unit': temp_item['material']['material_unit'],
                            'order_unit':temp_item['order_unit'],
                            'ordered_at': temp_item['ordered_at'],
                            'pr_id':temp_item['pr_id'],
                            'pr_no':temp_item['pr_no'],
                            'pr_item_no': temp_item['pr_item_no'],
                            'price_mode': temp_item['price_mode'],
                            'purchased_qty': temp_item['purchased_qty'],
                            'required_delivery_date':temp_item['required_delivery_date'],
                            # 如果是改的那一条物料required_qty 从Excel 而来
                            'required_qty':self.case_data['数据'][2]['required_qty'] if temp_item['material']['material_name'] == material_name else temp_item['required_qty'],
                            'sequence': temp_item['sequence'],
                            'status': temp_item['status'],
                            'tax_rate': temp_item['tax_rate'],
                            'to_purchase_qty': temp_item['to_purchase_qty']
                        })
            data = commons.dict_add(self.case_data['数据'][1], {
                'pr_id': pr_id,
                'ordered_by':global_data.data['mm']['customer_id'],#FIXME 
                'items':items
            })
            update_response = purchase_requirent.update(data)
            assert (update_response.status_code == 200)

    # 采购管理/采购申请列表 编辑采购申请单,新增一条物料
    class Add_item_ok__on_pr_list(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请列表/新增/编辑采购申请单', text)
        
        def run(self):
            # TODO pr_id从global_data.data['mm']['pr_list']['pr_id']中去拿
            pr_id = global_data.data['mm']['pr_list']['pr_id']
            # 这边先写死 pr_id = '999a4f3dead44ae9a061a29099959413'
            # pr_id = '999a4f3dead44ae9a061a29099959413'
            pr = purchase_requirent.get_detail({'pr_id':pr_id})
            assert(pr.status_code == 200)
            purchase_type = pr.json()['purchase_type']

            # 生成items参数
            items = []
            for i in range(len(pr.json()['items'])):
                temp_item = pr.json()['items'][i]
                items.append({
                    'field_values':[
                        {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300012','field_value':None},
                        {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300028','field_value':None},
                        {'field_no': "ED2021072300007", 'field_value': "打球", 'biz_type': "SPM_PR_ITEM"}
                    ],
                    'id': temp_item['id'],
                    'material_id':temp_item['material']['material_id'],
                    'material_no':temp_item['material']['material_no'],
                    'material_unit': temp_item['material']['material_unit'],
                    'order_unit':temp_item['order_unit'],
                    'ordered_at': temp_item['ordered_at'],
                    'pr_id':temp_item['pr_id'],
                    'pr_no':temp_item['pr_no'],
                    'pr_item_no': temp_item['pr_item_no'],
                    'price_mode': temp_item['price_mode'],
                    'purchased_qty': temp_item['purchased_qty'],
                    'required_delivery_date':temp_item['required_delivery_date'],
                    'required_qty':temp_item['required_qty'],
                    'select': False,
                    'sequence': temp_item['sequence'],
                    'status': temp_item['status'],
                    'tax_rate': temp_item['tax_rate'],
                    'to_purchase_qty': temp_item['to_purchase_qty']
                })
            # 新增物料
            material_list = material.retrieve(self.case_data['数据'][0])
            assert (material_list.status_code == 200)
            assert (len(material_list.json()['content']) > 0)

            material_id = material_list.json()['content'][0]['id']
            material_no = material_list.json()['content'][0]['material_no']
            order_unit = material_list.json()['content'][0]['material_purchase_unit']

            add_item = {
                'field_values':[
                    {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300012','field_value':None},
                    {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300028','field_value':None},
                    {'field_no': "ED2021072300007", 'field_value': "打球", 'biz_type': "SPM_PR_ITEM"}
                ],
                'material_id':material_id,
                'material_no':material_no,
                'order_unit': order_unit
                }
            items.append(commons.dict_add(add_item,self.case_data['数据'][1]))
            data = commons.dict_add({'items':items},
            {
                'pr_id':pr_id,
                'ordered_by': global_data.data['mm']['customer_id'],
                'purchase_type':purchase_type
            }
            )
            update_response = purchase_requirent.update(data)
            assert (update_response.status_code == 200)

    # 删除一行物料  
    class Delete_item_ok_on_pr_list(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请列表/删除/编辑采购申请单', text)
        
        def run(self):
            # TODO pr_id从global_data.data['mm']['pr_list']['pr_id']中去拿
            pr_id = global_data.data['mm']['pr_list']['pr_id']
            # 这边先写死 pr_id = '999a4f3dead44ae9a061a29099959413'
            # pr_id = '999a4f3dead44ae9a061a29099959413'
            pr=purchase_requirent.get_detail({'pr_id':pr_id})
            assert(pr.status_code == 200)
            purchase_type = pr.json()['purchase_type']

            # 需要删除的那一笔物料
            material_name = self.case_data['数据'][0]['物料名称']
            # 生成items参数
            items = []
            for i in range(len(pr.json()['items'])):
                temp_item = pr.json()['items'][i]
                if temp_item['material']['material_name'] != material_name:
                    items.append({
                        'field_values':[
                            {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300012','field_value':None},
                            {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300028','field_value':None},
                            {'field_no': "ED2021072300007", 'field_value': "打球", 'biz_type': "SPM_PR_ITEM"}
                        ],
                        'id': temp_item['id'],
                        'material_id':temp_item['material']['material_id'],
                        'material_no':temp_item['material']['material_no'],
                        'material_unit': temp_item['material']['material_unit'],
                        'order_unit':temp_item['order_unit'],
                        'ordered_at': temp_item['ordered_at'],
                        'pr_id':temp_item['pr_id'],
                        'pr_no':temp_item['pr_no'],
                        'pr_item_no': temp_item['pr_item_no'],
                        'price_mode': temp_item['price_mode'],
                        'purchased_qty': temp_item['purchased_qty'],
                        'required_delivery_date':temp_item['required_delivery_date'],
                        'required_qty':temp_item['required_qty'],
                        'sequence': temp_item['sequence'],
                        'status': temp_item['status'],
                        'tax_rate': temp_item['tax_rate'],
                        'to_purchase_qty': temp_item['to_purchase_qty']
                    })
            
            data = commons.dict_add({'items':items},
            {
                'pr_id':pr_id,
                'ordered_by': global_data.data['mm']['customer_id'],
                'purchase_type':purchase_type
            })
            update_response = purchase_requirent.update(data)
            assert (update_response.status_code == 200)

    class Print_invoice_ok_on_prm(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请管理/打印单据', text)
        
        def run(self):
            # TODO pr_id从global_data['mm']['pr_manage'][0]['pr_id']拿,这边单独测试，写死pr_id ：45601a64ffbd4a759e444f81fd388f19
            pr_id = global_data.data['mm']['pr_manage'][0]['pr_id']
            # pr_id = '45601a64ffbd4a759e444f81fd388f19'

            data = commons.dict_add(self.case_data['数据'][0],{'id':pr_id})
            r = invoice.create(data)
            assert (r.status_code == 200)
            assert (len(r.json()['signature']['pdf']) >= self.case_data['期望校验数据'][0])

    # 采购管理/采购申请管理 编辑一条数据，并且填入未税单价和含税单价
    class Edit_pr_ok_on_prm(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请管理/编辑', text)
        
        def run(self):
            # TODO pr_id从global_data['mm']['pr_manage'][0]['pr_id']拿,这边单独测试，写死pr_id ：45601a64ffbd4a759e444f81fd388f19
            pr_id = global_data.data['mm']['pr_manage'][0]['pr_id']
            # pr_id = '45601a64ffbd4a759e444f81fd388f19'

            #  根据pr_id get_detail  
            pr = purchase_requirent.get_detail({'pr_id':pr_id})
            assert(pr.status_code == 200)
            assert(len(pr.json()['id']) > 0)
            updated_material_name = self.case_data['数据'][0]['物料名称']

            # 原始查出来的items
            org_items = pr.json()['items']
            # 本次请求的请求体中的items
            new_items = []
            for index in range(len(org_items)):
                new_item={'field_values':[
                                            {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300012','field_value':None},
                                            {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300028','field_value':None},
                                            {'field_no': "ED2021072300007", 'field_value': "打球", 'biz_type': "SPM_PR_ITEM"}
                                        ]
                        }

                # 如果这笔item的material_no是需要修改的那一条
                if org_items[index]['material']['material_name'] == updated_material_name:
                    for key in org_items[index]:
                        if (key != 'material' and key != 'unit_price' and key != 'unit_tax_price') :
                            new_item[key] = org_items[index][key]
                        elif(key == 'unit_price' or key == 'unit_tax_price'):
                            new_item['unit_price'] = self.case_data['数据'][1]['未税单价']
                            new_item['unit_tax_price'] = self.case_data['数据'][1]['含税单价']

                        else:
                            new_item['material_id']=org_items[index]['material']['material_id']
                            new_item['material_no']=org_items[index]['material']['material_no']
                    # 最后判断是否有unit_price和unit_tax_price，没有的话手动加入
                    if not new_item.__contains__('unit_price'):
                        new_item['unit_price'] = self.case_data['数据'][1]['未税单价']
                    if not new_item.__contains__('unit_tax_price'):
                        new_item['unit_tax_price'] = self.case_data['数据'][1]['含税单价']
                    new_items.append(new_item)
                else:
                    for key in org_items[index]:
                        if (key != 'material') :
                            new_item[key]=org_items[index][key]
                        else:
                            new_item['material_id']=org_items[index]['material']['material_id']
                            new_item['material_no']=org_items[index]['material']['material_no']
                    new_items.append(new_item)
                body=commons.dict_add({
                    'items':new_items,
                    'pr_id':pr_id
                },self.case_data['数据'][2])
                r=purchase_requirent.update(body)
                assert (r.status_code == 200)


    #采购管理/采购订单管理/编辑PO/新增物料行 保存
    class Edit_po_add_material(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购订单管理/编辑PO/新增物料行', text)

        def run(self):
            #编辑的采购订单号从之前测试的新建采购订单获取
            po_no = global_data.data['mm']['po_manage']['po_no']
            po_list = purchase_order.retrieve({"po_no":po_no})
            assert (po_list.status_code == 200)
            assert (len(po_list.json()['content'])  != 0)
            id = po_list.json()['content'][0]['id']
            purchase_type = po_list.json()['content'][0]['purchase_type']
        
            supplier_id = po_list.json()['content'][0]['supplier_id']

            po = purchase_order.get_detail({"po_id":id})
            #supplier_email  = po.json()['supplier_email'] 
            ordered_by = po.json()['ordered_by']
            ordered_date = po.json()['ordered_date']
            local_currency_no = po.json()['local_currency_no']
            original_currency_no = po.json()['original_currency_no']

            assert(po.status_code == 200)    
            
            items = []

            for i in range(len(po.json()['items'])):
                temp_item = po.json()['items'][i]
                
                items.append({
                        "manual": True,
                        "id": temp_item['id'],
                        "item_numc": temp_item['item_numc'],
                        "po_id": temp_item['id'],
                        "po_item_no": temp_item['po_item_no'],
                        "supplier_id": temp_item['supplier_id'],
                        "supplier_name":  temp_item['supplier_name'],
                        "material_service_indicator": False,
                        #"receipt_storage_location_id": temp_item['receipt_storage_location_id'],
                        #"receipt_storage_location_no": temp_item['receipt_storage_location_no'],
                        #"receipt_storage_location_name": temp_item['receipt_storage_location_name'],
                        "required_delivery_date":  temp_item['required_delivery_date'],
                        "purchase_qty": temp_item['purchase_qty'],
                        "open_qty": temp_item['open_qty'],
                        "tax_rate": temp_item['tax_rate'],
                        "tax": temp_item['tax'],
                        "unit_price": temp_item['unit_price'],
                        "unit_tax_price": temp_item['unit_tax_price'],
                        "total_tax_price": temp_item['total_tax_price'],
                        "total_price": temp_item['total_price'],
                        "unit_tax": temp_item['unit_tax'],
                        "price_mode": "UNIT_PRICE",
                        "local_currency_no":temp_item['local_currency_no'],
                        "original_currency_no": temp_item['original_currency_no'],
                        "exchange_rate": 1,
                        "local_tax": temp_item['local_tax'],
                        "local_unit_tax_price": temp_item['local_unit_tax_price'],
                        "local_total_tax_price":temp_item['local_total_tax_price'],
                        "local_unit_price": temp_item['local_unit_price'],
                        "local_total_price": temp_item['local_total_price'],
                        "local_unit_tax":temp_item['local_unit_tax'],
                        "purchase_group": "PURHCASE_ONE",
                        "order_unit": temp_item['order_unit'],
                        "material_unit": temp_item['material']['material_unit'],
                        "select": False,
                        "material_id": temp_item['material']['material_id'],
                        "field_values": [
                            {
                                "field_no": "ED2021072300028",
                                "field_value": None,
                                "biz_type": "SPM_PO_ITEM"
                            }
                        ]
                })

            material_list = material.retrieve(self.case_data['数据'][0])
            assert (material_list.status_code == 200)
            assert (len(material_list.json()['content']) > 0)
            material_id = material_list.json()['content'][0]['id']
            material_no = material_list.json()['content'][0]['material_no']
            order_unit = material_list.json()['content'][0]['material_unit']

            purchase_qty = self.case_data['数据'][1]['purchase_qty']
            required_delivery_date = self.case_data['数据'][1]['required_delivery_date']
            tax_rate = self.case_data['数据'][1]['tax_rate']
            unit_price = self.case_data['数据'][1]['unit_price']
            add_item = {
                "field_values": [
                            {"field_no": "ED2021072300028","field_value": None,"biz_type": "SPM_PO_ITEM" }          
                        ],
                'manual': True,
                'material_id':material_id,
                'material_no':material_no,
                'purchase_qty': purchase_qty,
                "required_delivery_date": required_delivery_date,
                'tax_rate': tax_rate,
                #"tax": '100',
                "unit_price": unit_price,
                'order_unit': order_unit,
                # 'pr_item_id': 'manual-1',
                'select': False
            }
            items.append(add_item)
            data = commons.dict_add({'po_items':items},
            {
                'po_id':id,
                "id": id,
                "po_no": po_no,
                #'ordered_by': global_data.data['mm']['customer_id'],
                'ordered_by': ordered_by,
                'purchase_type':purchase_type,
                'exchange_rate':1,#FIXME 
                'supplier_id':supplier_id,
                #"supplier_email": supplier_email,
                "local_currency_no": local_currency_no,
                "original_currency_no": original_currency_no,
                "order_type": "N",
                "ordered_date": ordered_date,
            }
            )
            add_result = purchase_order.update(data)
            assert (add_result.status_code == 200)
                
    #采购管理/采购订单管理/编辑PO/删除PR行 保存
    class Edit_po_delete_pr(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购订单管理/编辑PO/删除PR行', text)
            
        def run(self):
            po_no = global_data.data['mm']['po_manage']['po_no']
            po_list = purchase_order.retrieve({"po_no":po_no})
            assert(po_list.status_code == 200)
            assert (len(po_list.json()['content']) >= self.case_data['期望校验数据'][0])
            id = po_list.json()['content'][0]['id']        
        
            purchase_type = po_list.json()['content'][0]['purchase_type']
            

            po = purchase_order.get_detail({'po_id':id})
            supplier_id =  po.json()['supplier_id'] 
            #supplier_email  = po.json()['supplier_email'] 
            ordered_by = po.json()['ordered_by']
            ordered_date = po.json()['ordered_date']
            local_currency_no = po.json()['local_currency_no']
            original_currency_no = po.json()['original_currency_no']


            assert (po.status_code == 200)
            material_name = self.case_data['数据'][0]['物料名称']
            items = []
            for i in range(len(po.json()['items'])):
                temp_item = po.json()['items'][i]
                if temp_item['material']['material_name'] != material_name:
                    items.append({
                        "manual": True,
                        "id": temp_item['id'],
                        "item_numc": temp_item['item_numc'],
                        "po_id": temp_item['id'],
                        "po_item_no": temp_item['po_item_no'],
                        "supplier_id": temp_item['supplier_id'],
                        "supplier_name":  temp_item['supplier_name'],
                        "material_service_indicator": False,
                        #"receipt_storage_location_id": temp_item['receipt_storage_location_id'],
                        #"receipt_storage_location_no": temp_item['receipt_storage_location_no'],
                        #"receipt_storage_location_name": temp_item['receipt_storage_location_name'],
                        "required_delivery_date":  temp_item['required_delivery_date'],
                        "purchase_qty": temp_item['purchase_qty'],
                        "open_qty": temp_item['open_qty'],
                        "tax_rate": temp_item['tax_rate'],
                        "tax": temp_item['tax'],
                        "unit_price": temp_item['unit_price'],
                        "unit_tax_price": temp_item['unit_tax_price'],
                        "total_tax_price": temp_item['total_tax_price'],
                        "total_price": temp_item['total_price'],
                        "unit_tax": temp_item['unit_tax'],
                        "price_mode": "UNIT_PRICE",#FIXME 
                        "local_currency_no":temp_item['local_currency_no'],
                        "original_currency_no": temp_item['original_currency_no'],
                        "exchange_rate": 1,
                        "local_tax": temp_item['local_tax'],
                        "local_unit_tax_price": temp_item['local_unit_tax_price'],
                        "local_total_tax_price":temp_item['local_total_tax_price'],
                        "local_unit_price": temp_item['local_unit_price'],
                        "local_total_price": temp_item['local_total_price'],
                        "local_unit_tax":temp_item['local_unit_tax'],
                        "purchase_group": "PURHCASE_ONE",#FIXME 
                        "order_unit": temp_item['order_unit'],
                        "material_unit": temp_item['material']['material_unit'],
                        "select": False,
                        "material_id": temp_item['material']['material_id'],
                        "field_values": [
                            {
                                "field_no": "ED2021072300028",
                                "field_value": None,
                                "biz_type": "SPM_PO_ITEM"
                            }
                        ]

                    })   
            data = commons.dict_add({'po_items':items},
            {
                'po_id':id,
                "id": id,
                "po_no": po_no,
                'ordered_by': ordered_by,
                'purchase_type':purchase_type,
                'exchange_rate':1,
                'supplier_id': supplier_id,
                #"supplier_email": supplier_email,
                "local_currency_no": local_currency_no,
                "original_currency_no": original_currency_no,
                "order_type": "N",#FIXME 
                "ordered_date": ordered_date,
                "remark": None,
                "supplier_visible": False,
                #"ordered_by": "ea65a9003aaa49549810af8a69970ef9",
                "back_to_pr_flag": True
            }
            )
            delete_result = purchase_order.update(data)
            assert (delete_result.status_code == 200)


    #物料在货源清单没有维护供应商，新增采购申请单时 选择物料不会带出供应商信息
    class Add_pr_material_no_supplier(Abstract_case):#FIXME 
    
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请列表/新建采购申请单/物料没有维护供应商', text)
        def run(self):
            material_list = material.retrieve(self.case_data['数据'][0])
            assert (material_list.status_code == 200)
            assert (len(material_list.json()['content']) > 0)
            id = material_list.json()['content'][0]['id']
            material_no = material_list.json()['content'][0]['material_no']
            field_value = {}
            item = {
                "pr_item_id": None,
                "manual": True,
                "item_numc": None,
                "project_no": None,
                "project_name": None,
                "supplier_name": None,
                "required_qty": "2",
                "purchased_qty": None,
                "required_delivery_date": "2021-09-20",
                "purchase_group": None,
                "remark": None,
                "select": False,
                "order_unit_vo": {
                    "version": 8,
                    "created_by": "d88a5a6e32b54076a4a500423646cf95",
                    "created_date": "2021-07-13T16:26:05",
                    "last_modified_by": "d88a5a6e32b54076a4a500423646cf95",
                    "last_modified_date": "2021-07-14T10:55:11",
                    "id": "8103204705550532608",
                    "unit_no": "BM",
                    "unit_name": "BM",
                    "unit_code": "BM",
                    "dimension_id": "10034001",
                    "display_decimal": 8,
                    "rounding_decimal": 8,
                    "enable": True
                },
                "material_id": id,
            
                "order_unit": "BM",
                "field_values": [
                    {'biz_type': 'SPM_PR_ITEM', 'field_no': 'ED2021072300012', 'field_value': None},
                    {'biz_type': 'SPM_PR_ITEM', 'field_no': 'ED2021072300028', 'field_value': None}
                ]
            }

            data = commons.dict_add({'items': [item]}, {'ordered_by': global_data.data['mm']['customer_id'],
                                                        'org_id': None,
                                                        'purchase_type': '110',
                                                        'remark': None})
            r = purchase_requirent.create(data)
            assert (r.status_code == 200)
            assert (material_list.json()['suppliers'].length() == 0)
        
            

    class Export_pr_list_ok_on_pr_list(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请列表/导出/编辑采购申请单', text)
        
        def run(self):
            # TODO pr_id从global_data.data['mm']['pr_list']['pr_id']中去拿
            pr_id = global_data.data['mm']['pr_list']['pr_id']
            # 这边先写死 pr_id = '999a4f3dead44ae9a061a29099959413'
            # pr_id = '999a4f3dead44ae9a061a29099959413'

            excel_response = purchase_requirent.export_excel({'pr_id':pr_id})
            assert(len(excel_response.text) > 0)
            # output = StringIO(excel_response.text)
            # import xlwt
            # import xlwt
            # book = xlwt.Workbook(encoding='utf-8')
            # （此处省略一些写excel操作。。。）
            # output = StringIO.StringIO()
            # book.save(output)
            
            # print(output)

            # import xlrd
            # book = xlrd.open_workbook(file_contents=str(excel_response.text))
            # sh = book.sheet_by_index(0)
            # print("{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols))
            # print("Cell D30 is {0}".format(sh.cell_value(rowx=29, colx=3)))
            # for rx in range(sh.nrows):
            #     print(sh.row(rx))
            

    class Create_pr_with_default_suppliers_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请列表/新建采购申请单/默认供应商', text)
        
        def run(self):
            material_list = material.retrieve(self.case_data['数据'][0])
            assert (material_list.status_code == 200)
            assert (len(material_list.json()['content']) > 0)
            material_id = material_list.json()['content'][0]['id']
            material_no = material_list.json()['content'][0]['material_no']
            order_unit = material_list.json()['content'][0]['material_purchase_unit']

            items=[]
            items.append({
                'field_values':[
                    {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300012','field_value':None},
                    {'biz_type':'SPM_PR_ITEM','field_no':'ED2021072300028','field_value':None},
                    {'field_no': "ED2021072300007", 'field_value': "打球", 'biz_type': "SPM_PR_ITEM"}
                ],
                'required_qty':self.case_data['数据'][1]['required_qty'],
                'required_delivery_date':self.case_data['数据'][1]['required_delivery_date'],
                'material_id': material_id,
                'material_no': material_no,
                'order_unit': order_unit
            })
            # 请求body
            body = commons.dict_add({
                # 'ordered_by': global_data.data['mm']['customer_id'],
                'ordered_by': global_data.data['mm']['customer_id'],

                'items':items
            },self.case_data['数据'][2])

            r = purchase_requirent.create(body)
            assert (r.status_code == 200)
            assert (len(r.json()['new_id']) > 0)
            new_id = r.json()['new_id']
            # 将采购申请列表里面的创建的采购申请单的id放到global_data里面
            pr_dict = {'pr_id':new_id}
            pr_list = {'pr_list':pr_dict}
            if (global_data.data.__contains__('mm')):
                global_data.data['mm']['pr_list']=pr_dict
            else:
                global_data.data['mm'] = pr_list

            # get pr_detail by pr_id
            pr_detail = purchase_requirent.get_detail({'pr_id':new_id})
            assert (pr_detail.status_code == 200)
            assert (str(pr_detail.json()['suppliers'][0]['name']).find(str(self.case_data['期望校验数据'][0])) >= 0)
            
    class Print_invoice_ok_on_prl(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请列表/打印单据', text)
        
        def run(self):
            # pr = purchase_requirent.retrieve(self.case_data['数据'][0])
            # assert(pr.status_code == 200)
            # assert (len(pr.json()['content']) >= self.case_data['期望校验数据'][0])

            # id = pr.json()['content'][0]['pr_id']
            id = global_data.data["mm"]["pr_list"]["pr_id"]
            # id = "e40019a3fc7f402d96f6f07529252c86"
            data=commons.dict_add(self.case_data['数据'][0],{'id':id})
            r=invoice.create(data)
            assert (r.status_code == 200)
            assert (len(r.json()['signature']['pdf']) >= self.case_data['期望校验数据'][0])

    class  Add_po_item_material_has_supplierAndPrice(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购订单管理/新建采购订单/物料维护了供应商和价格', text)
    
        def run(self):
            material_list = material.retrieve(self.case_data['数据'][0])
            assert (material_list.status_code == 200)
            assert (len(material_list.json()['content']) > 0)
            
            material_id = material_list.json()['content'][0]['id']
            order_unit = material_list.json()['content'][0]['material_purchase_unit']
            # 根据material_id查价格信息
            price_info = price_record.retrieve({'material_id':material_id})
            assert(len(price_info.json()['content']) > 0)
            po_item={
                'manual':True,
                # 价格纪录带出
                "unit_price" : price_info.json()['content'][0]['unit_price'],
                "unit_tax_price" : price_info.json()['content'][0]['unit_tax_price'],
                "tax_rate" : price_info.json()['content'][0]['tax_rate'],
                
                "required_delivery_date": self.case_data['数据'][1]['required_delivery_date'],
                "purchase_qty": self.case_data['数据'][1]['purchase_qty'],
                "material_id": material_id,
                "order_unit": order_unit,
                # 自定义字段
                "field_values": 
                [{
                'field_no': "ED2021072300007", 
                'field_value': "打球", 
                'biz_type': "SPM_PO_ITEM"
                }]
            }
            # 查询供应商信息
            supplier_id = price_info.json()['content'][0]['supplier_id']
            supplier_info = supplier.retrieve({"supplier_id":supplier_id})
            #assert(supplier_info.json()[0]['id'])
            #supplier_id = supplier_info.json()[0]['id']
            # 请求body
            body=commons.dict_add({
                'ordered_by':global_data.data['mm']['customer_id'],
                'ordered_date':'2021-08-24T17:24:27',
                "supplier_id": supplier_id,
                'po_items':[po_item]
            },self.case_data['数据'][3]) 

            r=purchase_order.create(body)
            assert (r.status_code == 200)
            
            

    class Create_po_without_pr_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购订单管理/手动创建PO/不选PR', text)
        
        def run(self):
            
            material_list = material.retrieve(self.case_data['数据'][2])
            assert (material_list.status_code == 200)
            assert (len(material_list.json()['content']) > 0)

            material_id = material_list.json()['content'][0]['id']
            order_unit = material_list.json()['content'][0]['material_purchase_unit']
            po_item={
                'manual':True,
                "unit_price": self.case_data['数据'][1]['unit_price'],
                "tax_rate": self.case_data['数据'][1]['tax_rate'],
                "unit_tax_price": self.case_data['数据'][1]['unit_tax_price'],
                "required_delivery_date": self.case_data['数据'][1]['required_delivery_date'],
                "purchase_qty": self.case_data['数据'][1]['purchase_qty'],
                "material_id": material_id,
                "order_unit": order_unit,
                # 自定义字段爱好
                "field_values": 
                [{
                'field_no': "ED2021072300007", 
                'field_value': "打球", 
                'biz_type': "SPM_PO_ITEM"
                }]
            }
            # 供应商
            supplier_info = supplier.retrieve(self.case_data['数据'][3])
            assert(supplier_info.json()[0]['id'])

            supplier_id = supplier_info.json()[0]['id']
            # 请求body
            body=commons.dict_add({
                'ordered_by':global_data.data['mm']['customer_id'],
                'ordered_date':'2021-08-24T17:24:27',
                "supplier_id": supplier_id,
                'po_items':[po_item]
            },self.case_data['数据'][0]) 

            r=purchase_order.create(body)
            assert (r.status_code == 200)

            # 将创建出来的PO放到global_data
            po_id = r.json()['new_id']
            po_info = purchase_order.get_detail({'po_id':po_id})

            po_no = po_info.json()['po_no']
            po_manage = {'po_id':po_id,'po_no':po_no}
            global_data.data['mm']['po_manage']=po_manage
    class Create_po_with_pr_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购订单管理/手动创建PO/选择PR', text)
        
        def run(self):
            
            material_list = material.retrieve(self.case_data['数据'][2])
            assert (material_list.status_code == 200)
            assert (len(material_list.json()['content']) > 0)

            material_id = material_list.json()['content'][0]['id']
            order_unit = material_list.json()['content'][0]['material_purchase_unit']

            pr_id = global_data.data["mm"]["pr_manage"][1]["pr_id"]
            pr_info = purchase_requirent.get_detail({"pr_id":pr_id})

            pr_item_id = pr_info.json()["items"][0]["id"]
            po_item={
                "unit_price": self.case_data['数据'][1]['unit_price'],
                "tax_rate": self.case_data['数据'][1]['tax_rate'],
                "unit_tax_price": self.case_data['数据'][1]['unit_tax_price'],
                "required_delivery_date": self.case_data['数据'][1]['required_delivery_date'],
                "purchase_qty": self.case_data['数据'][1]['purchase_qty'],
                "material_id": material_id,
                "order_unit": order_unit,
                "pr_id" : pr_id,
                "pr_item_id" :pr_item_id,
                "pr_links" : [{"pr_id":pr_id ,"pr_item_id":pr_item_id}],
                # "pr_item_id" 
                # 自定义字段爱好
                "field_values": 
                [{
                'field_no': "ED2021072300007", 
                'field_value': "打球", 
                'biz_type': "SPM_PO_ITEM"
                }]
            }
            # 供应商
            supplier_info = supplier.retrieve(self.case_data['数据'][3])
            assert(supplier_info.json()[0]['id'])

            supplier_id = supplier_info.json()[0]['id']
            # 请求body
            body=commons.dict_add({
                'ordered_by':global_data.data['mm']['customer_id'],
                'ordered_date':'2021-08-24T17:24:27',
                "supplier_id": supplier_id,
                'po_items':[po_item]
            },self.case_data['数据'][0]) 

            r = purchase_order.create(body)
            assert (r.status_code == 200)

    class Create_po_with_price_ok(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购订单管理/手动创建PO/带出价格纪录', text)
        
        def run(self):
            material_list = material.retrieve(self.case_data['数据'][2])
            assert (material_list.status_code == 200)
            assert (len(material_list.json()['content']) > 0)

            material_id = material_list.json()['content'][0]['id']
            order_unit = material_list.json()['content'][0]['material_purchase_unit']
            # 根据material_id查价格纪录
            price_info = price_record.retrieve({'material_id':material_id})
            assert(len(price_info.json()['content']) > 0)
            po_item={
                # 价格纪录带出
                "unit_price" : price_info.json()['content'][0]['unit_price'],
                "unit_tax_price" : price_info.json()['content'][0]['unit_tax_price'],
                "tax_rate" : price_info.json()['content'][0]['tax_rate'],
                
                "required_delivery_date": self.case_data['数据'][1]['required_delivery_date'],
                "purchase_qty": self.case_data['数据'][1]['purchase_qty'],
                "material_id": material_id,
                "order_unit": order_unit,
                # 自定义字段爱好
                "field_values": 
                [{
                'field_no': "ED2021072300007", 
                'field_value': "打球", 
                'biz_type': "SPM_PO_ITEM"
                }]
            }
            # 供应商
            supplier_id = price_info.json()['content'][0]['supplier_id']
            # 请求body
            body=commons.dict_add({
                'ordered_by': global_data.data['mm']['customer_id'],
                'ordered_date': commons.get_current_T_time(),
                # 可以自己获取
                "supplier_id": supplier_id,
                'po_items':[po_item]
            },self.case_data['数据'][0]) 

            r=purchase_order.create(body)
            assert (r.status_code == 200)


    class Export_pr_manage_ok_on_pr_list(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请管理/导出/编辑采购申请单', text)
        
        def run(self):
            pr_id = global_data.data["mm"]["pr_manage"][0]["pr_id"]
            excel_response = purchase_requirent.export_excel({'pr_id':pr_id})
            assert(len(excel_response.text) > 0)

    class Pr_invert_po_ok_supplier_not_null(Abstract_case):
        def __init__(self, text=None) -> None:
            super().__init__('采购管理/采购申请管理/批量转换', text)
        
        def run(self):
            pr_id = global_data.data["mm"]["pr_manage"][0]["pr_id"]
            pr_detail = purchase_requirent.get_detail({"pr_id":pr_id})

            pr_no = pr_detail.json()["pr_no"]
            pr_invert = purchase_order.purchase_requirent_retrieve({"pr_no":pr_no})
            id = pr_invert.json()['content'][0]['id']
            data={'purchaseRequestItemIds':[id]}
            
            #转换方法batch_create_selected中传参是id，而不是pr_id ,需要在详情里找pr_no ,根据po_no找到id
            r=purchase_order.batch_create_selected(data)
            assert (r.status_code == 200)
            assert (r.json()["success_count"] == 1) #TODO

manager=Manager()