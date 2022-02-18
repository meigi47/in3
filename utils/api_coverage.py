'''
里面显示的是已实施的interface中占据apidoc里面对应模块的接口覆盖率，具有是否区分访问方法两种口径
相对于测试离线处理，输出到 result/api_coverage.csv
csv
module,coverage_involving_method,coverage_involving_path
'''
import os 
import yaml 
from utils.commons import find_apidoc
from utils.commons import read_yml

def coverage():#result={module:{cov1:1,cov2:2}}
    result={}
    #modules
    applyed_modules=[x[:-5] for x in os.listdir('interface/api')]

    interfaced_url={}

    for module_name in applyed_modules:
        interfaced_url[module_name]={}
        interfaced_module=interfaced_url[module_name]
        

        apidoc=find_apidoc(module_name)['paths']
        for i in list(apidoc.keys()):
            if 'private' in i:
                del apidoc[i]

        interfaced=read_yml(f'interface/api/{module_name}.yaml')  

        
        for i in interfaced.values():
            for j in i.values():
                try:
                    url=j.get('url')
                except:
                    print(f"异常数据 {str(j)}")
                    exit()
                if not url: continue 
                if url not in interfaced_module: interfaced_module[url]=set([j.get('type')])
                else: interfaced_module[url].add(j.get('type'))
        #interfaced_module{url:{get,post}}
        len_apidoc_involved_method=0
        for i in apidoc.values():
            len_apidoc_involved_method+=len(i)

        len_interfaced_involved_method=0
        for i in interfaced_module.values():
            len_interfaced_involved_method+=len(i)
                

        result[module_name]={
            'coverage_involving_method':str(round(len_interfaced_involved_method/len_apidoc_involved_method*100,2)),
            'coverage_involving_path':str(round(len(interfaced_module)/len(apidoc)*100,2)),
        }


            
#    return result

#def gen_csv(data:dict,file_path='result/api_coverage.csv') :
    file_path='result/api_coverage.csv'
    with open(file_path,'w',encoding='GB2312') as fp:
        line=['module','coverage_involving_method(%)','coverage_involving_path(%)']#先写标题
        fp.write(','.join(line)+'\n')

        for module_name,indexs in result.items():
            line=[module_name,indexs['coverage_involving_method'],indexs['coverage_involving_path']]
            fp.write(','.join(line)+'\n')


