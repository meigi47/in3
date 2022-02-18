# 没有依赖的小工具代码
import os
import re
import time
from typing import *
import datetime
import pytest
import yaml

from utils.logger import Logger

def get_current_T_time()->str:
    return str(datetime.datetime.now().isoformat())

def folder_assure(path: str):  # 确保文件夹存在，若不存在则新建
    pass

def read_yml(target: str):  # yml读取文件
    try:
        with open(target, 'r', encoding='utf8') as fs:
            content = yaml.full_load(fs)
            return content
    except Exception as e:
        Logger.warning(f'{repr(e)}')
        return {}


def tryer(self, fn):
    t0 = time.time()
    while True:
        if time.time()-t0 > self.general_timeout:
            pytest.raises(TimeoutError)
        else:
            try:
                fn()
                break
            except:
                continue


def conv_time(self, tim=None) -> str:  # 转换数字时间戳为格式化字符串,为空则取当时时间
    if None == tim:
        tim = time.time()
    return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tim)))


def name_convert_to_camel(name: str) -> str:
    """下划线转驼峰(小驼峰)"""
    return re.sub(r'(_[a-z])', lambda x: x.group(1)[1].upper(), name)


def name_convert_to_snake(name: str) -> str:
    """驼峰转下划线"""
    if '_' not in name:
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
    # else:
    #     raise ValueError(f'{name}字符中包含下划线，无法转换')
    return name.lower()


def name_convert(name: str) -> str:
    """驼峰式命名和下划线式命名互转"""
    is_camel_name = True  # 是否为驼峰式命名
    if '_' in name and re.match(r'[a-zA-Z_]+$', name):
        is_camel_name = False
    elif re.match(r'[a-zA-Z]+$', name) is None:
        raise ValueError(f'Value of "name" is invalid: {name}')
    return name_convert_to_snake(name) if is_camel_name else name_convert_to_camel(name)


def dict_add(d1: dict, *d2: tuple) -> dict:  # 拼接多个字典，单层相加，有同名字段元素时，dic2覆盖dic1
    for i in d2:
        if not i : continue
        for key, value in i.items():
            if key not in d1:
                d1[key] = value
            else:
                if isinstance(value, dict):
                    dict_add(d1[key], value)
                else:
                    d1[key] = value
    return d1

def dict_key_replace_key_word(target_dict: dict, from_key_word: str, to_key_word: str) -> dict: # 替换字典中key的关键字
    new_dict = {}
    for key, value in target_dict.items():
        new_key = key.replace(from_key_word, to_key_word)
        new_dict[new_key] = value
    return new_dict

def recur_folder_for_file(root_path:str,regex:str)->list:#递归查找文件并返回文件path列表,但是这里是对它的文件名进行部分的正则匹配
    result=[]
    gen = os.walk(root_path)
    for root, folders, files in gen:
        for file in files:
            if re.search(regex,file):
            # if file.endswith(component+'.yaml'):
                result.append(os.path.join(root, file))
    return result

def find_apidoc(component: str) -> dict:  # 根据组件名找文件
    result=recur_folder_for_file('apidoc',f'{component}.ya*ml$')
    if len(result) == 0:
        Logger.warning(f'找不到模块{component}对应的api文档,确定library中的模块名称是否正确')
        return None
    elif len(result) >= 2:
        Logger.warning(f'找到多个模块{component}对应的api文档,确定library中的模块名称是否正确')
        Logger.warning(f'错误结果{str(result)}')
    return read_yml(result[0])

    # 如果找到了两个同名的就报警告，并返回第一个找到的文件内容
    # 如果一个也没有就返回None


def get_ref_difinition(tmp_ref: str, yml_text) -> dict:  # TODO路径解析完善,返回ref声明的节点
    tmp = tmp_ref.replace('#', '').split('/')
    return yml_text[tmp[1]][tmp[2]]


# data {type,schema,name,in} 找到api文档对应节点的type
def param_find_type(data: dict, yml_text) -> str:
    if not data:
        return None
    if data.get('type'):
        return data.get('type')
    else:
        if data.get('$ref'):
            tmp_ref = data.get('$ref')
        elif data.get('schema', {}).get('type'):
            return data.get('schema', {}).get('type')
        elif data.get('schema', {}).get('$ref'):
            tmp_ref = data.get('schema').get('$ref')
        else:
            Logger.error(f'意外的api文档节点类型，没有找到对应的type！{str(data)}')
            return None
        # $ref: '#/definitions/SalesOrderListItemVO'
        return param_find_type(get_ref_difinition(tmp_ref, yml_text), yml_text)
        
def get_case_data_path(data:dict):#data就是case data里面的一则用例
    return data.get("测试用例集", "") + '/' + data.get("标题", "")

# 根据apidoc生成空的 body 或者 parameter或者其他header,path是doc文档短path
def req_content_gen(data: dict) -> dict:
    if not data:
        return None
    # 因为默认是library比较靠前的处理流程，所以使用覆盖处理相关参数,默认生成的数据可能比较表层，需要library进一步填充
    # data {method,path,component,case_data}->{header,body,query,method,path,component,case_data}
    
    def get_empty_result(data_type: str):  # 根据传入的类型声明返回输出
        result = None
        #'string'  'integer' 'boolean'
        if data_type == 'array':
            result = []
        elif data_type == 'object':
            result = {}
        return result

    doc = find_apidoc(data['component'])
    api_doc = doc['paths'][data['path']][data['method']]
    # 处理header
    header = {}
    if api_doc.get('consumes'):
        header['Accept'] = api_doc.get('consumes')[0]
    if api_doc.get('produces'):
        header['Content-Type'] = api_doc.get('produces')[0]
    # 处理params
    query = {}
    for i in api_doc['parameters']:
        if i['in'] == 'query':
            query[i['name']] = None
    # 处理body,VO#TODO递归与必填处理
    # TODO VO类型的list数据还是需要由library层传入
    body = {}
    elements = []
    for i in api_doc['parameters']:
        if i['in'] == 'body':
            elements.append(i)
    if len(elements) == 1:
        if param_find_type(elements[0], doc) == 'object':
            tmp_difinition_prop = get_ref_difinition(
                elements[0].get('schema').get('$ref'), doc)['properties']
            for i in tmp_difinition_prop:
                body[name_convert_to_snake(i)] = get_empty_result(
                    param_find_type(tmp_difinition_prop[i], doc))
        elif param_find_type(elements[0], doc) == 'array':
            body = list(data.get('case_data').values())[0]
        else:
            # tmp_type = param_find_type(elements[0], doc)
            # body[name_convert_to_snake(elements[0]['name'])] = get_empty_result(tmp_type)
            Logger.error(f"{__name__}遇到了意外的参数类型")
    elif len(elements) == 0:
        pass
    elif len(elements) >= 1:
        for i in elements:
            tmp_type = param_find_type(i, doc)
            body[name_convert_to_snake(i['name'])] = get_empty_result(tmp_type)
    else:
        Logger.error(f'意外的接口文档信息，{__name__}生成空白请求模板失败!')

    return dict_add(data, {'header': header, 'query': query, 'body': body})





if __name__ == "__main__":
    content = read_yml("case_data.yml")
    print(content)
