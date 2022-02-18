from interface.abstract_prod_op import Abstract_production_obj


class Price_record(Abstract_production_obj):
    def __init__(self) -> None:
        self.data = {}
        self.module = "mm"
        self.operation = "price_record"

    
price_record = Price_record()