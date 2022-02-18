#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time


class Param_to_method_handler:
    def __init__(self):
        self.data = {}

    def start_timestamp(self, method_name: str) -> str:
        if method_name not in self.data:
            self.data[method_name] = str(int(time.time()))

        return self.data[method_name]


param_to_method_handler = Param_to_method_handler()
