#配置pytest
# from utils.logger import Logger
# from functools import wraps
# from utils import commons
# from utils.global_data import global_data
import pytest



# def adjust_order(source_list:list,source_position,target_position:int):
#     if source_position==target_position:
#         return 
#     operat_obj=source_list[source_position]
#     source_list.pop(source_position)
#     source_list.insert(target_position-1 if source_position<target_position else target_position,operat_obj)



def pytest_collection_modifyitems(config, items):
    '''
    casepath_no0_order1_needskip
    no:同用例下的excel数据实例编号
    order：同测试集下的顺序编号,有这个编号的用例会在collect完毕之后进行顺序调整，使用简单的遍历插入法
    needskip:用例跳过标记
    '''
    print(f'collected {str(len(items))} items')
    
    for item in items:
        if 'needskip' in item.name:
            item.add_marker(pytest.mark.skip())
        order_in_suite11=[i[5:] for i in item.name.split('_') if i.startswith('order')]
        # print(order_in_suite11)
        # print(item.name)
        if not order_in_suite11:
            print(f'存在异常的item：{item.name}！！')
            exit()
        else:
            order_in_suite=order_in_suite11[0]
            if  order_in_suite: item.add_marker(pytest.mark.run(order=int(order_in_suite)))
    

# def pytest_itemcollected(item):#刚刚完成了一个item的collect
#     pass 




