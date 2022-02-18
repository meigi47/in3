'''
from utils import api_coverage

api_coverage.coverage()

from utils.url_perf import url_perf

url_perf.gen_perf_result()
'''
'''
from utils.yaml_utils import * 
'''
#xlsx2yaml('case_data','case_data')   
#yaml2xlsx('case_data','case_data')  

from utils.mapper import Mapper

Mapper.from_apidoc_to_mapper("pp.yaml","swagger.yaml")
