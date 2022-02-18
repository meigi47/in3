#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
from utils.mapper import Mapper as factor_mapper
import os

class Demand_supply(Abstract_production_obj):
    def __init__(self) -> None:
      self.data = {}
      self.module = "pp"
      self.operation = "demand_supply"

    def get_demand_supply(self, data: dict,unique_instruction="get_demand_supply"):
      tmp = global_data.join_url_type(
         data, self.module, self.operation, unique_instruction)
      return request_manager.do_request(tmp)


demand_supply=Demand_supply()