import ShippingPrice
class AbstractShipping(object):
    def __init__(self):
        self.zones = {}
        self.prices = {}
        self.maxSizeFixedPrice = None
    def checkCountry(self, country):
        raise ValueError("Not Implemented")
    def calculate(self, zone, weight):
        raise ValueError("Not Implemented")
    def findZone(self, zone):
        raise ValueError("Not Implemented")