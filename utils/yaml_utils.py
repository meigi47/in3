from utils.excel_utils import excel_load
from utils.commons import read_yml, recur_folder_for_file
import yaml
import os


'''
考虑到git管理xlsx会有问题，现在yaml是执行与调试测试时所需的，当要进行管理汇报时可以export到xlsx
'''

# yaml -> xlsx; 离线函数，要更新xlsx用于管理时使用
def yaml2xlsx(yaml_path:str,xlsx_path:str): 
    '''
    yaml_path: yaml用例文件夹
    xlsx_path: xlsx用例文件夹
    '''
    yaml_abs=recur_folder_for_file(yaml_path,r'\.ya*ml') 
    count=0
    for i in yaml_abs :
        tmp=read_yml(i)
        if not tmp: 
            print(f"{i} 读取失败!跳过……")
            continue 
        else:
            excel_file=os.path.join(xlsx_path,os.path.basename(i).replace('.yaml','.xlsx').replace('.yml','.xlsx'))  
            print(f'正在写入{excel_file}……')
            excel_load.write_wk(tmp,excel_file)
            count+=1
    print(f'yaml转excel完毕，共计{count}文件')


#xlsx -> yaml; 离线函数，第一次从excel初始化yaml用例时使用
def xlsx2yaml(xlsx_path:str,yaml_path:str):
    excels_abs=recur_folder_for_file(xlsx_path,'.xlsx$')
    count=0
    print(excels_abs)
    for i in excels_abs :
        tmp=excel_load.load_wk(i)
        if not tmp: 
            print(f"{i} 读取失败!跳过……")
            continue 
        else:
            yaml_file=os.path.join(yaml_path,os.path.basename(i).replace('.xlsx','.yaml'))
            print(f'正在写入{yaml_file}……')
            with open(yaml_file,'w',encoding='utf8') as fp :
                yaml.dump(tmp,stream=fp,allow_unicode=True)
            count+=1
    print(f'yaml转excel完毕，共计{count}文件')



#yaml -> list ; 在线函数，正常执行用例时使用
#utils.commons.read_yml