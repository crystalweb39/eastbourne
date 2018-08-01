from AbstractShipping import *
from ShippingPrice import *
import math

class AustraliaPostInternational(AbstractShipping):
    
    
    def __init__(self):
        super(AustraliaPostInternational, self).__init__()
        # lists of the Australian postcodes which match to a zone
        # For simplicity we don't calculate the lower price for some postcodes 
        self.zones["A"] = "New Zealand".lower().split(",")
        self.zones["B"] = "China,Fiji,Hong Kong,India,Indonesia,Japan,South Korea,Malaysia,New Caledonia,Papua New Guinea,Philippines,Singapore,Solomon Islands,Sri Lanka,Taiwan,Thailand,Vietnam".lower().split(",")
        self.zones["C"] = "Canada,Israel,USA".lower().split(",")
        self.zones["D"] = "Austria,Belgium,Denmark,Finland,France,Germany,Greece,Ireland,Italy,Malta,Netherlands,Norway,Poland,South Africa,Spain,Sweden,Switzerland,United Kingdom".lower().split(",")
        #                                 perkg                   per article                    maxfixed  zone
        self.prices["A"] = ShippingPrice({0: 14.01, 2001: 7.36}, {0: 2.71, 2001: 15.25}, 0, "A")
        self.prices["B"] = ShippingPrice({0: 18.34, 2001: 9.41}, {0: 2.71, 2001: 19.38}, 0, "B")
        self.prices["C"] = ShippingPrice({0: 22.66, 2001: 13.59}, {0: 2.71, 2001: 19.43}, 0, "C")
        self.prices["D"] = ShippingPrice({0: 27.08, 2001: 18.05}, {0: 3.28, 2001: 19.95}, 0, "D")
    def checkCountry(self, country):
        country = country.lower().strip()
        for x in self.zones.keys():
            if self.zones[x].count(country):
                return True
        return False
    def calculate(self, zone, weight):
        return self.prices[zone].getPrice(weight)*1.1
    def findZone(self, zone):
        zone = zone.strip().lower()
        for x in self.zones.keys():
            if self.zones[x].count(zone):
                return x
                break
if __name__ == "__main__":
    p = AustraliaPostInternational()
    zone = p.findZone("New Zealand")
    print zone
    price = p.calculate(zone, 10)
    print price
    