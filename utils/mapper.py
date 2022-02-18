from logging import Logger
import os
import shutil

import yaml
from utils.commons import name_convert_to_snake, read_yml
from utils.global_data import global_data


class Mapper:  # TODO VO的递归处理
    def read_mapper_from_file(component_name, path, method):
        # mappers = read_yml(os.path.join(
        #     "utils","map_accordance", component_name+".yaml"))
        mappers=global_data.find_mapper(component_name)
        mappers["params"] = mappers["paths"].get(path).get(method, {})
        return mappers

    def get_by_alias(mappers, case_alias):
        '''
        查询case_alias对应的后端请求参数

        Returns:
            查询该case_alias返回dict eg.{"name":"xxx", "in":"yyy"}
            查无此case_alias返回None
        '''
        params_mapper = mappers["params"]
        definition_mapper = mappers["definitions"]
        schema_ref_list = []
        for param in params_mapper:  # 遍历第一层mapper
            if param['case_alias'] == case_alias or param["name"] == case_alias or name_convert_to_snake(param["name"]) == case_alias:
                return param
            ref = param.get("schema", {}).get("$ref")
            if ref:
                schema_ref_list.append(
                    f'{param["in"]}/{ref.split("/")[-1]}')  # 记录位置信息
        for ref in schema_ref_list:  # 若params未包含该case_alias, 则继续在definitions中查找
            vo_name = ref.split("/")[-1]
            vo = definition_mapper[vo_name]
            for param_name, param_info in vo.items():
                if param_info["case_alias"] == case_alias or case_alias == param_name or name_convert_to_snake(param_name) == case_alias:
                    param_info["name"] = param_name
                    param_info["in"] = "body"  # TODO 多重VO无法处理
                    return param_info
                ref = param_info.get("$ref")
                if ref:
                    schema_ref_list.append(ref)

    def update_case_data(mappers, data:dict):  # data里面可能有 query、header、body
        if isinstance(data['body'],list):return
        case_data = data["case_data"]
        case_name_list = list(case_data.keys())
        for case_name in case_name_list:
            api_data = Mapper.get_by_alias(mappers, case_name)
            if api_data:
                api_name = name_convert_to_snake(api_data["name"])
                where = api_data["in"]
                assert(where =='query' or where == 'body')#如果参数里面乱传入了path的参数而没有删除会造成问题，下面的句子会取到url报错
                data[where][api_name] = case_data[case_name]

    def map(data):
        if isinstance(data["case_data"],list):     #传参为list: [] 
            data['body'] = data['case_data']   
            return data

        mappers = Mapper.read_mapper_from_file(
            data.get("component"), data.get("path"), data.get("method"))
        Mapper.update_case_data(mappers, data)
        return data

    def get_case_alias_from_paths(paths_mapper, url, method_name, param_name):
        if not paths_mapper:
            return None
        methods = paths_mapper.get(url, {})
        params = methods.get(method_name, {})
        for param in params:
            if param["name"] == param_name or name_convert_to_snake(param["name"]) == param_name:
                return param["case_alias"]
        return None

    def get_case_alias_from_definitions(definitions_mapper, definition_name, property_name):
        if not definitions_mapper:
            return None
        property_data = definitions_mapper.get(
            definition_name, {}).get(property_name, {})
        if property_data:
            return property_data['case_alias']
        return None

    def from_apidoc_to_mapper(file_path_from, file_path_to, old_mapper_path=None):
        raw_data = read_yml(file_path_from)
        old_mapper = read_yml(old_mapper_path)

        paths = raw_data["paths"]
        result = {}
        for url, operation in paths.items():
            for method_name, method_data in operation.items():
                parameters = method_data.get("parameters", {})
                for parameter in parameters:
                    case_alias = Mapper.get_case_alias_from_paths(
                        old_mapper['paths'], url, method_name, parameter["name"]) if old_mapper_path else None
                    parameter["case_alias"] = case_alias

        definitions = raw_data["definitions"]
        for definition_name, definition_value in definitions.items():
            properties = definition_value.get("properties")
            if properties:
                for property_name, property_data in properties.items():
                    property_data["case_alias"] = Mapper.get_case_alias_from_definitions(
                        old_mapper['definitions'], definition_name, property_name)  if old_mapper_path else None
        result = {
            "paths": {
                url_path: {
                    method_name: method_data.get("parameters", {})
                    for method_name, method_data in operation.items()
                }
                for url_path, operation in paths.items()
            },
            "definitions": {
                definition_name: definition_value["properties"]
                for definition_name, definition_value in definitions.items()
                if definition_value.get("properties")
            }
        }

        # 加个备份,默认覆盖
        if os.path.exists(file_path_to):
            shutil.copyfile(file_path_to, file_path_to+'.backup')

        with open(file_path_to, "w", encoding="utf-8") as f:
            yaml.dump(result, f, default_flow_style=False, allow_unicode=True)
