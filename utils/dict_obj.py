from utils.commons import dict_add


class Dict_obj:  # 保守封装的字典
    '''
    这只是一个抽象的供各处自行初始化的一个模板类，不要全局初始化
    '''
    def __init__(self, data: dict = None) -> None:
        self.private_data = {} if not data else data

    def add(self, data: dict) -> None:  # 增加private_data
        self.private_data = dict_add(self.private_data, data)

    def get(self) -> dict:  # 传回假private_data供查询判断
        return self.private_data

    def delete(self, keys: list) -> None:  # 批量删除private_data，跳过不存在的键值
        for i in keys:
            if i in self.private_data.keys():
                del(self.private_data[i])


