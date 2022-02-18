基于pytest的IN3 api测试框架

## 结构简介

interface:	业务封装
manager:	流程控制
util:	工具
config:	配置文件
result:	输出结果
constants:	常量

## 初始化工程



### 安装工具环境

`pip install -r ./requirements.txt` 

额外安装   `allure` 最新版本    https://github.com/allure-framework/allure2/releases



### VSCode中配置pytest

`"python.testing.pytestEnabled": true`  

### 测试执行

工程主目录下直接执行 `pytest` 



## 添加用例

### 添加case数据与代码

### 刷新apidoc 与 map_accordance（非必需）

apidoc是后端工程直接导出的swgger文档，为yaml格式，经过`utils.mapper.Mapepr.from_apidoc_to_mapper` 处理之后，输出到map_accordance文件夹中，用于进行接口字段的映射，通俗的讲就是汉字与接口参数名的互转

### 添加codedef

`codedef`，准确来讲是IN3中的下拉查询，各部分初始化记载于`interface`中的`cofa`与分散的各个模块里面，在utils中的`global_data`中统一被调用执行



### 额外处理

工程具有一些独立于测试运行的内容，即不在测试过程中执行的函数，大致可以称为“离线函数”，目前将功能与调用代码列出，典型调用方式是在根目录执行：

```python
from utils import api_coverage

api_coverage.coverage()   #生成api覆盖率

from utils.url_perf import url_perf

url_perf.gen_perf_result()   #生成性能统计


from utils.yaml_utils import * 
xlsx2yaml('path_to_yaml','path_to_excel')   #将excel用例转为yaml用例
```







