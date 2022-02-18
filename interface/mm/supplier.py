from interface.abstract_prod_op import Abstract_production_obj


class Supplier(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "mm"
        self.operation = "supplier"

supplier = Supplier()