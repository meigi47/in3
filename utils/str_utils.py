#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast
import json
import re
from utils.logger import Logger
from utils.handler.param_to_method_handler import param_to_method_handler


class Str_utils:

    def __init__(self) -> None:
        self.BRACES_REG = r'\{(.*?)\}'

    def get_placeholder_str(self, text: str) -> list:
        """
        传入{}类型字符串,返回{}内容的数组
        """
        str = re.findall(self.BRACES_REG, text)
        return str

    def replace_placeholder_str(self, text: str):
        """
        专用的碎片数据处理,携带{}中内容请求方法得到返回值并替换{}内容
        """
        if text is None: return text
        placeholder_str_list = self.get_placeholder_str(text)
        placeholder_str_list_len = len(placeholder_str_list)
        if placeholder_str_list_len > 0:
            for i in range(placeholder_str_list_len):
                method_name = placeholder_str_list[i]
                result_str = getattr(
                    param_to_method_handler,
                    method_name
                )(method_name)
                text = text.format(**{method_name: result_str})
        return text

    def json_str_to_list(self, json_str: str) -> list:
        if json_str is None:
            return json_str
        try:
            return json.loads(json_str)
        except:
            Logger.error(f'json转换失败：{json_str}')
            exit()

    def json_list_to_str(self, json_list):
        if json_list is None:
            return json_list
        return json.dumps(json_list, ensure_ascii=False)

    def str_to_auto_type(self, targer_str: str):
        if targer_str is None:
            return targer_str
        return ast.literal_eval(targer_str)

    def get_id_name_in_path(self,path:str):#取倒数最后一个不为tenent_id的变量，若findall取到的>2 ，日志报警
        id_candidates=self.get_placeholder_str(path)
        if len(id_candidates)>2: Logger.warning(f"未考虑的情况:从path提取大括号参数时发现两个以上的变量{path}")
        target_id_name=None
        for i in reversed(id_candidates):
            if i != "tenant_id":
                target_id_name = i 
                break
        return target_id_name


str_utils = Str_utils()

if __name__ == "__main__":
    str = "{name}{name2}"
    # print(type(str))
    str_utils.replace_placeholder_str(str)
