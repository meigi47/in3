#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils.commons as commons
from manager.request_manager import request_manager
from utils.commons import *
from utils.global_data import global_data
from utils.str_utils import str_utils
from interface.abstract_prod_op import Abstract_production_obj
class Contract(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "mm"
        self.operation = "contract"

    
contract = Contract()