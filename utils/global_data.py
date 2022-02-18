#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
全局上下文与codedef初始化
'''

from utils.logger import Logger
import os
from utils.commons import find_apidoc,read_yml

class Global_data:
    def __init__(self) -> None:
        self.data = {}
        
        self.code_def = self.data["code_def"] = {}
        self.code_def_index = self.data["code_def_index"] = {}
        self.code_def_inited = False

        self.docs={}
        self.docs_inited=False


    def code_def_init(self):#调取各大interface里面的code def init
        from interface.mm.currency import currency
        currency.init_global_data_codedef()
        from interface.cofa.codedef import code_def
        code_def.init_global_data_codedef()
        from interface.md.mdm_material import material
        material.init_material_groups_codedef()
        material.init_material_unit_groups_codedef()
        self.code_def_inited=True

    def query_code_def(self,data)->str:#{结算币种:人民币} return 156
        if not self.code_def_inited: self.code_def_init()
        key,value=list(data.items())[0]
        if key in self.code_def_index.keys():
            index=self.code_def_index.get(key)
            body_list = self.code_def[index['code_def_key']]
            for obj in body_list:
                if obj[index['in_key']] == value:
                    return obj[index['out_key']]
            Logger.warning(f'所查询的code def类型有记录，但没有查到对应转换的条目:{str(data)}')
            return value
        else:
            return value

    def doc_init(self):
        '''
        从interface/api拿module，然后内存里面放一下apidoc map_accordance interface
        '''
        module_files=os.listdir('interface/api')
        modules=[x[:-5] for x in module_files ]
        for module in modules:
            self.docs[module]={}
            self.docs[module]['apidoc']=find_apidoc(module)
            self.docs[module]['map_accordance']=read_yml(os.path.join(
            "utils","map_accordance", module+".yaml"))
            self.docs[module]['interface']=read_yml(os.path.join("interface","api", module + ".yaml"))

        self.docs_inited=True

    def find_apidoc(self,component:str):#从内存取doc的方法
        if not self.docs_inited:self.doc_init()
        if self.docs_inited:
            return self.docs[component]['apidoc']

    def find_mapper(self,component:str):#从内存取doc的方法
        if not self.docs_inited:self.doc_init()
        if self.docs_inited:
            return self.docs[component]['map_accordance']

    def find_interface(self,component:str):#从内存取doc的方法
        if not self.docs_inited:self.doc_init()
        if self.docs_inited:
            return self.docs[component]['interface']
    

    def join_url_type(self,case_data, module, operation, method):
        api_info = self.find_interface(module)
        param = api_info.get(operation).get(method)
        url = param["url"]
        type = param["type"]
        tmp = {
            'header': {},
            'query': {},
            'path': url,
            'body': {},
            'method': type,
            'component': module,
            'case_data': case_data
        }
        return tmp

    
global_data = Global_data()