#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 数据抽取与汇总	Util层复用，base调用	脱胎于日志模块的即时轻量过程信息处理，可以用来诊断、动态进度等

import logging
import sys
import time
from os import makedirs
from os.path import dirname, exists
from pprint import pformat

loggers = {}

LOG_ENABLED = True  # 是否开启日志
LOG_TO_CONSOLE = False  # 是否输出到控制台
LOG_TO_FILE = True  # 是否输出到文件

LOG_PATH = 'result/logs/runtime-%s.log' % time.strftime("%Y%m%d")   # 日志文件路径
LOG_LEVEL = 'DEBUG'  # 日志最低级别
LOG_FORMAT = '%(asctime)s | %(levelname)s | process: %(process)d | %(filename)s | %(module)s | %(funcName)s [line: %(lineno)d] | %(message)s'  # 每条日志输出格式
DATA_FORMAT = '%Y-%m-%d %H:%M:%S'

# 日志
# TODO再加入调取统计处理的内容 1
# TODO由配置走的日志路径


class Log:
    def __init__(self, unique_name='mytest'):  # unique name用于保持不和其他日志串流
        global loggers
        self.logger = None

        if not unique_name:
            unique_name = __name__

        if loggers.get(unique_name):
            self.logger = loggers.get(unique_name)
            return

        self.logger = logging.getLogger(unique_name)
        self.logger.setLevel(LOG_LEVEL)

        # 输出到控制台
        if LOG_ENABLED and LOG_TO_CONSOLE:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setLevel(level=LOG_LEVEL)
            formatter = logging.Formatter(LOG_FORMAT, datefmt=DATA_FORMAT)
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

        # 输出到文件
        if LOG_ENABLED and LOG_TO_FILE:
            # 如果路径不存在，创建日志文件文件夹
            log_dir = dirname(LOG_PATH)
            if not exists(log_dir):
                makedirs(log_dir)
            # 添加 FileHandler
            file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8', mode='a')
            file_handler.setLevel(level=LOG_LEVEL)
            formatter = logging.Formatter(LOG_FORMAT, datefmt=DATA_FORMAT)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # 保存到全局 loggers
        loggers[unique_name] = self.logger

    # def info(self, info: str):
    #     self.logger.info(pformat(info))

    # def warning(self, info: str):
    #     self.logger.warning(pformat(info))

    # def error(self, info: str):
    #     self.logger.error(pformat(info))

    # def debug(self, info: str):
    #     self.logger.debug(pformat(info))

    # def error_exit(self, info: str):
    #     self.error(info)
    #     print(f"重大错误:{str(info)}")
    #     exit()


Logger = Log().logger