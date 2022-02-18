
from utils.logger import Logger
from copy import deepcopy as dcp
import datetime
from utils.config import config


class Api_performance:

    '''
    一份在进行接口请求时自动做的性能日志 result/perf_log.csv
    一份独立于测试执行的生成的汇总性能结果 result/perf_result.csv
    使用extra.py执行
    '''

    def __init__(self) -> None:
        self.perf_log='result/perf_log.csv'
        self.perf_result='result/perf_result.csv'
        self.logfile=open(self.perf_log,'w',encoding='gb2312')

        self.perf_log_param=['env','module','path','method','cost_s','req_time']
        self.perf_result_param=['env','module','path','method','cost_avg_s','num_records']

    
    # def __del__(self):
    #     self.logfile.close()

    def gen_perf_result(self):#从性能日志里面汇总,不在测试流程里面调用！！
        data={}
        with open(self.perf_log,'r') as fp:
            if not fp:
                print('暂时没有性能文件记录,先跑跑测试看看')
                return 
            lines=fp.read().splitlines()
            for line in lines[1:]:
                splited=line.split(',')
                new_line=[x for x in splited  if x!='']
                env,module,path,method,cost_s,req_time = new_line
                cost_s=float(cost_s)
                key=','.join([env,module,path,method])
                num_records=1 if key not in data else data[key]['num_records']+1
                cost_avg_s=cost_s if key not in data else (data[key]['cost_avg_s']*data[key]['num_records']+cost_s)/num_records
                data[key]={'cost_avg_s':cost_avg_s,'num_records':num_records }

        with open(self.perf_result,'w',encoding='gb2312') as fp:
            line=self.perf_result_param
            fp.write(','.join(line)+'\n')
            
            for i in data:
                line=','.join([i,str(data[i]['cost_avg_s']),str(data[i]['num_records'])])
                fp.write(line+'\n')
        
        

    def log_perf(self,module,path,method,req_time:float,res_time:float):#仅用于实时记录
        env=config.base_data['selected_env']
        cost_s=res_time-req_time
        req_time=str(datetime.datetime.fromtimestamp(req_time))
        output1=[env,module,path,method,cost_s,req_time]
        output2=[str(x) for x in output1]
        self.logfile.write(','.join(output2)+'\n')

url_perf=Api_performance()