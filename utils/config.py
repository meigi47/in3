import utils.commons as commons


class Config:  # 这个过程较为简单，就不拓展了，配置使用原始的存储就好,
    def __init__(self) -> None:
        self.base_data = commons.read_yml('config/main.yml')
        self.case_file_path = self.base_data["case_file_path"]

        tmp = self.base_data['selected_env']
        self.env_data = commons.read_yml(f'config/envs/{tmp}.yml')


config = Config()
