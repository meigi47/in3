import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.logger import Logger
from interface.abstract_prod_op import  Abstract_production_obj
from utils.global_data import global_data
from utils.mapper import Mapper
from interface.mm.bom import bom


class Material(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "md"
        self.operation = "mdm_material"
    
    def material_groups_retrieve(self, data: dict) -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "material_groups_retrieve")
        return request_manager.do_request(tmp)

    def material_unit_groups_retrieve(self, data: dict) -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "material_unit_groups_retrieve")
        return request_manager.do_request(tmp)

    def material_units_retrieve_by_measure_unit_groups(self, data: dict) -> dict:
        #此处因id的in值为path，无法直接传递，需要将id直接转为值。
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "material_units_retrieve_by_measure_unit_groups")
        #下面过程可做参考
        Logger.info("这是传入req mgr的数据")
        Logger.info(tmp)
        if isinstance(tmp["case_data"],list):     #传参为list: [] 
            tmp['body'] = tmp['case_data']   
            return tmp
        mappers = Mapper.read_mapper_from_file(
            tmp.get("component"), tmp.get("path"), tmp.get("method"))
        tmp = self.replace_path(tmp)#只可在此处做关于case_data中有在path数据的替换修改，若在之前调用，无法获得mappers
        Mapper.update_case_data(mappers, tmp)
        Logger.info("这是map之后的数据")
        Logger.info(tmp)
        return request_manager.do_request_withdata(tmp)

    def material_unit_groups_page(self, data: dict) -> dict:
        tmp = global_data.join_url_type(
            data, self.module, self.operation, "material_unit_groups_page")
        return request_manager.do_request(tmp)

    def init_material_groups_codedef(self):
        repos = self.material_groups_retrieve({})
        assert repos.status_code==200
        assert len(repos.json())>0
        # 实际存放的code_def数据
        global_code_def = global_data.data["code_def"]
        global_code_def[self.module + "material_groups"] = []
        for repo in repos.json():
            global_code_def[self.module + "material_groups"].append(repo["code_def"])
        # code_def的索引名，供index匹配用
        global_code_def_index = global_data.data["code_def_index"]
        index_names = ["物料类别"]
        for index_name in index_names:
            global_code_def_index[index_name] = {
                'code_def_key':(self.module + "material_groups"),
                'in_key':'name',
                'out_key':'code'
            }    


    def init_material_unit_groups_codedef(self):
        repos = self.material_unit_groups_retrieve({"enable":True})
        assert repos.status_code==200
        assert len(repos.json())>0
        # 实际存放的code_def数据
        global_code_def = global_data.data["code_def"]
        global_code_def[self.module + "material_unit_groups"] = []
        for repo in repos.json():
            global_code_def[self.module + "material_unit_groups"].append(repo)
        # code_def的索引名，供index匹配用
        global_code_def_index = global_data.data["code_def_index"]
        index_names = ["计量单位组"]
        for index_name in index_names:
            global_code_def_index[index_name] = {
                'code_def_key':(self.module + "material_unit_groups"),
                'in_key':'unit_group_name',
                'out_key':'unit_group_no'
            }  


    def get_bom_from_casedata(self,data):
        #该方法实现获取测试数据中的物料BOM信息
        #该方法返回一个列表，每一个元素是一个父物料和其子物料 BOM数量的关系
        #如[{'A': [{'B': 1}, {'C': 1}]}],表示A的子物料为B*1和C*1
        BOM_info=[]
        if len(data)==0:
            Logger.info("测试数据未给出BOM信息")
        else:
            for bom in data:
                write=0
                if len(BOM_info)!=0:
                    for bominfo in BOM_info:
                        if bom["parent"] in bominfo:#已在BOM_info有该父物料的信息
                            tmp={}
                            tmp[bom["children"]]=bom["number"]
                            bominfo[bom["parent"]].append(tmp)
                            write=1
                            break
                        else:
                            pass
                    if write==1:
                        continue
                    else:
                        tmp={}
                        tmp[bom["parent"]]=[]
                        tmp_info={}
                        tmp_info[bom["children"]]=bom["number"]
                        tmp[bom["parent"]].append(tmp_info)
                        BOM_info.append(tmp)
                else:
                    tmp={}
                    tmp[bom["parent"]]=[]
                    tmp_info={}
                    tmp_info[bom["children"]]=bom["number"]
                    tmp[bom["parent"]].append(tmp_info)
                    BOM_info.append(tmp)
        return BOM_info

    def update_bom(self,data):
        #该方法实现根据给出的物料BOM信息，维护系统中的物料BOM
        for key,value in data.items():
            material_no=key
            time.sleep(60)#创建完物料后，mysql->es有10s的等待时间，需要加上等待时间，不然容易查不出物料的数据，下面同理
            
            r=self.retrieve({"material_no":material_no})
            assert (r.status_code == 200)
            if r.json()['total_elements'] == 0:
                Logger.info("未查到对应的物料"+material_no)
                pytest.fail()
            material_id=r.json()['content'][0]["id"]
            #获取父物料的BOM
            r=bom.get_bom_material_new({"material_id":material_id})
            material_bom_info=r.json()
            #包装BOM信息
            bom_components=[]
            material_ids=[]
            for children in value:
                for key,value_1 in children.items():
                    #time.sleep(10)
                    r=self.retrieve({"material_no":key})
                    assert (r.status_code == 200)
                    if r.json()['total_elements'] == 0:
                        Logger.info("未查到对应的物料"+key)
                        pytest.fail()
                    m_id=r.json()['content'][0]["id"]
                    material_ids.append(m_id)
            
            r=bom.get_boms_info({"material_ids":material_ids,"bom_usage":1})#此处接口修改，原先该接口为获取物料详情，目前改为创建BOM，不用该接口
            assert (r.status_code == 200)
            assert len(r.json()) != 0
            item_numc=10
            for child_info in r.json():
                child_info["material"]["material_unit_vo"]=child_info["material_unit_vo"]
                #child_info["material"]["material_id"]=child_info["material_id"]
                child_info["material"]["item_numc"]=item_numc
                for children in value:
                    if child_info["material"]["material_no"] in children:
                        child_info["material"]["quantity"]=children[child_info["material"]["material_no"]]
                child_info["material"]["status"]="add"
                child_info["material"]["relevant_sales_indicator"]=True
                child_info["material"]["relevant_engineer_indicator"]=True
                child_info["material"]["relevant_production_indicator"]=True
                child_info["material"]["relevant_costing_indicator"]=True
                child_info["material"]["folder_name_path"]=None
                child_info["material"]["id"]=str(int(time.time()))
                bom_components.append(child_info["material"])
                item_numc=item_numc+10
            material_bom_info["bom_components"]=bom_components
            material_bom_info["is_new_bom"]=True
            material_bom_info["bom_structure_type"]="STD"
            material_bom_info["valid_from_date"]=material_bom_info["material"]["valid_from_date"]
            material_bom_info["valid_to_date"]=material_bom_info["material"]["valid_to_date"]
            material_bom_info["bom_usage"]=1
            r=bom.update_boms(material_bom_info)
            assert (r.status_code == 200)
    
    def change_bom(self,data):
        #该方法实现根据给出的物料BOM信息，维护系统中的物料BOM
        for key,value in data.items():
            material_no=key
            time.sleep(30)#创建完物料后，mysql->es有10s的等待时间，需要加上等待时间，不然容易查不出物料的数据，下面同理
            r=self.retrieve({"material_no":material_no})
            assert (r.status_code == 200)
            if r.json()['total_elements'] == 0:
                Logger.info("未查到对应的物料"+material_no)
                pytest.fail()
            material_id=r.json()['content'][0]["id"]
            #获取父物料的BOM
            #此处需考虑一个情况：实际上父物料没有BOM,那此过程则和原先的添加bom一致
            r=bom.get_bom_material_new({"material_id":material_id})
            material_bom_info=r.json()


            if 'bom_components' in material_bom_info:#该物料已有bom
                item_numc=r.json()['bom_components'][len(r.json()['bom_components'])-1]["item_numc"]+10#BOM行号，获取之前的行号，然后改为现在的行号
            else:
                item_numc=10
            #包装BOM信息
            bom_components=[]
            material_ids=[]
            for children in value:
                for key,value_1 in children.items():
                    #time.sleep(10)
                    r=self.retrieve({"material_no":key})
                    assert (r.status_code == 200)
                    if r.json()['total_elements'] == 0:
                        Logger.info("未查到对应的物料"+key)
                        pytest.fail()
                    m_id=r.json()['content'][0]["id"]
                    material_ids.append(m_id)
            
            r=bom.get_boms_info({"material_ids":material_ids,"bom_usage":1})
            assert (r.status_code == 200)
            assert len(r.json()) != 0
            #item_numc=10
            for child_info in r.json():
                child_info["material"]["material_unit_vo"]=child_info["material_unit_vo"]
                #child_info["material"]["material_id"]=child_info["material_id"]
                child_info["material"]["item_numc"]=item_numc
                for children in value:
                    if child_info["material"]["material_no"] in children:
                        child_info["material"]["quantity"]=children[child_info["material"]["material_no"]]
                child_info["material"]["status"]="add"
                child_info["material"]["relevant_sales_indicator"]=True
                child_info["material"]["relevant_engineer_indicator"]=True
                child_info["material"]["relevant_production_indicator"]=True
                child_info["material"]["relevant_costing_indicator"]=True
                child_info["material"]["folder_name_path"]=None
                child_info["material"]["id"]=str(int(time.time()))
                bom_components.append(child_info["material"])
                item_numc=item_numc+10
            
            if  'bom_components' in material_bom_info:
                del material_bom_info["bom_components"]
                material_bom_info["bom_components"]=bom_components
                material_bom_info["is_new_bom"]=True
                material_bom_info["bom_structure_id"]=material_bom_info["id"]
                #material_bom_info["bom_structure_type"]="STD"
                #material_bom_info["valid_from_date"]=material_bom_info["material"]["valid_from_date"]
                #material_bom_info["valid_to_date"]=material_bom_info["material"]["valid_to_date"]
                del material_bom_info["tenant_id"]
                Logger.info(material_bom_info)
            else:
                material_bom_info["bom_components"]=bom_components
                material_bom_info["is_new_bom"]=True
                material_bom_info["bom_structure_type"]="STD"
                material_bom_info["valid_from_date"]=material_bom_info["material"]["valid_from_date"]
                material_bom_info["valid_to_date"]=material_bom_info["material"]["valid_to_date"]
                material_bom_info["bom_usage"]=1
            r=bom.update_boms(material_bom_info)
            assert (r.status_code == 200)

    def get_bom_from_wo_detail(self,data):
        #该方法通过传入的工单详情，获取当前的工单bom，返回一个如[{'A': [{'B': 1}, {'C': 1}]}]的列表去表示bom
        bom_list=[]
        #bom_list.append({data["material"]["material_no"]:[]})#每个工单会有一个主物料，先做此的处理
        self.recursion_get_bom(data["kitting_items"],data["material"]["material_no"],bom_list)
        Logger.info(bom_list)
        return bom_list

    def recursion_get_bom(self,data,parent,bom_list):
        #循环组装bom信息
        for child in data:
            if len(bom_list)==0:#未有数据
                bom_list.append({parent:[{child["kitting_material"]["material_no"]:child["bom_qty"]}]})
            else:
                write=0
                for bom in bom_list:#列表中找到父节点对应的子节点列表
                    if parent in bom:
                        bom[parent].append({child["kitting_material"]["material_no"]:child["bom_qty"]})
                        write=1
                    else:
                        pass
                if write==0:
                    bom_list.append({parent:[{child["kitting_material"]["material_no"]:child["bom_qty"]}]})
            if "children" in child:#子物料也有子物料的情况
                self.recursion_get_bom(child["children"],child["kitting_material"]["material_no"],bom_list)        

    def recursiom_mixed_bom_data(self,data,level,sequence,parent_id,last_child):
        #封装创建工单时，子物料的数据
        num=len(data)
        location=1
        ls=[]
        if len(last_child)!=0:
            for lls in last_child:
                ls.append(lls)
        for bom_data in data:
        #id需要修改
            ls=[]
            if len(last_child)!=0:
                for lls in last_child:
                    ls.append(lls)
            if "sp_procurement_type" in bom_data:#第一层BOM
                del bom_data["sp_procurement_type"]
            if "procurement_type" in bom_data:
                del bom_data["procurement_type"]  
            if level==1:#第一层BOM
                del bom_data["parent_material_id"]
                ls.clear()
            else:
                bom_data["parent_id"]=parent_id
            bom_data["level"]=level
            bom_data["id"]=bom_data["id"]+"_"+ str(sequence)
                
            #del child["procurement_type"]
            
            bom_data["kitting_status"]=0
            bom_data["sequence"]=sequence
            bom_data["expanded"]=True
            bom_data["location"]=True
            row=20+sequence
            sequence=sequence+1
            bom_data["xid"]="row_"+ str(row)
            if location==num:
                ls.append(True)
                bom_data["last_child"]=ls
            else:
                ls.append(False)
                bom_data["last_child"]=ls
            if "children" in bom_data:
                sequence=self.recursiom_mixed_bom_data(bom_data["children"],level+1,sequence,bom_data["id"],ls)
                bom_data["leaf"]=False
            else:
                bom_data["children"]=[]
                bom_data["leaf"]=True
            location=location+1
        return sequence




material = Material()
