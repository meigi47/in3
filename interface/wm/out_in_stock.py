#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from utils.commons import *

from interface.abstract_prod_op import Abstract_production_obj


class Out_in_stock(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "wm"
        self.operation = "out_in_stock"

out_in_stock = Out_in_stock()