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
from utils.mapper import Mapper


class Mrp_rules(Abstract_production_obj):
   def __init__(self) -> None:
      self.data = {}
      self.module = "pp"
      self.operation = "mrp_rules"


mrp_rules=Mrp_rules()