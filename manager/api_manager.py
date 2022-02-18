import json

import utils.commons as commons
import requests
from utils.config import config
from utils.logger import Logger
from utils.url_perf import url_perf
import time
from utils.global_data import global_data


class Api_manager:  # 包装api相关因素，如进行采集、操作api文档等
    def join_api_path(
        self, data: dict
    ) -> str:  # 根据接口文档 component+path合成接口路径,tenantid   data {'path_param':{'account_id':xxxxxxxx}}
        tenant_id = config.env_data['login_info']['tenant_id']
        doc = global_data.find_apidoc(data['component'])
        result = config.env_data['api-server'] + '/service' + doc[
            'basePath'] + data['path'].replace('{tenant_id}', str(tenant_id))
        if 'path_param' in data:
            path_param = data['path_param']
            result = result.format(**path_param)
            Logger.info('合并后的URL' + result)
        return result

    def do_request(self, data: dict) -> dict:
        original_path=data['path'] 
        data['path'] = self.join_api_path(data)
        if 'Content-Type' in data.keys(
        ) and 'application/json' in data['Content-Type']:
            data['body'] = data['body'].json()
        request_data = {}
        request_data['url'] = data['path']
        request_data['params'] = data['query']
        request_data['headers'] = data['header']
        request_data['data'] = json.dumps(data['body'])
        request_data['method'] = data['method']
        if 'files' in data.keys():
            request_data['files '] = data['files ']
        Logger.info('>>request:')
        Logger.info(request_data)
        Logger.info('>>response:')
        
        req_time=time.time()
        result = requests.request(
            **request_data, timeout=config.base_data['api_timeout'])
        res_time=time.time()

        perf_param={
            'module':data['component'],
            'path':original_path,
            'method':data['method'],
            'req_time':req_time,
            'res_time':res_time
        }
        url_perf.log_perf(**perf_param)

        Logger.info(result.text)
        
        return result


api_manager = Api_manager()
