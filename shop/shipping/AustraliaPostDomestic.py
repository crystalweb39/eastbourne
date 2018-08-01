from AbstractShipping import *
from ShippingPrice import *
import math

class AustraliaPostDomestic(AbstractShipping):
    def __init__(self):
        super(AustraliaPostDomestic, self).__init__()
        self.countries = ["australia",]
        # lists of the Australian postcodes which match to a zone
        # For simplicity we don't calculate the lower price for some postcodes 
        self.zones["N1"] = range(1000, 2264)+range(2500, 2531)+range(2555, 2575)+range(2740, 2787)+[2890]
        self.zones["N2"] = range(200, 300)+range(2485, 2500)+range(2531, 2555)+range(2575, 2640)+range(2640, 2648)+range(2649, 2715)+[2716]+range(2720, 2731)+range(2787, 2879)+range(2881, 2890)+range(2891, 2899)+range(2900, 3000)
        self.zones["V1"] = range(3000, 3221)+range(3335, 3342)+range(3425, 3443)+range(3750, 3812)+range(3910, 3921)+range(3926,3945)+range(3972,3979)+range(3980,3984)+range(8000,8999)
        self.zones["V2"] = range(3221,3335)+range(3342,3424)+range(3444,3689)+range(3689,3691)+range(3691,3750)+range(3812,3910)+range(3921,3926)+range(3945,3972)+[3979]+range(3984,4000)
        self.zones["Q1"] = range(4000,4225)+[4225]+range(4225,4300)+range(4500,4550)+range(9000,9300)+range(9400,9597)+range(9700,9799)
        self.zones["Q2"] = range(4300,4450)+range(4550,4700)+range(9597,9600)+range(9880,9920)
        self.zones["Q3"] = range(4450,4500)+range(4700,4806)+range(9920,9960)
        self.zones["Q4"] = range(4806,4900)+range(9960,10000)
        self.zones["S1"] = range(5000,5200)+range(5800,6000)
        self.zones["S2"] = range(5200,5750)
        self.zones["NT1"] = range(800,1000)
        self.zones["W1"] = range(6000,6215)+range(6800,7000)
        self.zones["W2"] = range(6215,6700)
        self.zones["W3"] = range(6700,6800)
        self.zones["T1"] = range(7000,8000)
        #                                 perkg                   per article                    maxfixed  zone
        self.prices["N1"] = ShippingPrice({0: 0, 251: 0, 500: 0}, {0: 4.35, 251: 5.1, 500: 5.8}, 500, "N1")
        self.prices["N2"] = ShippingPrice({0: 0, 251: 0, 500: 0.36}, {0: 4.35, 251: 5.5, 500: 7.45}, 500, "N2")
        self.prices["V1"] = ShippingPrice({0: 0, 251: 0, 500: 0.49}, {0: 4.35, 251: 5.5, 500: 7.35}, 500, "V1")
        self.prices["V2"] = ShippingPrice({0: 0, 251: 0, 500: 0.66}, {0: 4.35, 251: 5.5, 500: 8.5}, 500, "V2")
        self.prices["Q1"] = ShippingPrice({0: 0, 251: 0, 500: 0.49}, {0: 4.35, 251: 5.5, 500: 7.35}, 500, "Q1")
        self.prices["Q2"] = ShippingPrice({0: 0, 251: 0, 500: 0.83}, {0: 4.35, 251: 5.5, 500: 8.5}, 500, "Q2")
        self.prices["Q3"] = ShippingPrice({0: 0, 251: 0, 500: 1.11}, {0: 4.35, 251: 5.5, 500: 8.5}, 500, "Q3")
        self.prices["S1"] = ShippingPrice({0: 0, 251: 0, 500: 0.57}, {0: 4.35, 251: 5.5, 500: 7.35}, 500, "S1")
        self.prices["S2"] = ShippingPrice({0: 0, 251: 0, 500: 0.87}, {0: 4.35, 251: 5.5, 500: 8.5}, 500, "S2")
        self.prices["W1"] = ShippingPrice({0: 0, 251: 0, 500: 1.44}, {0: 4.35, 251: 5.5, 500: 7.35}, 500, "W1")
        self.prices["W2"] = ShippingPrice({0: 0, 251: 0, 500: 1.8}, {0: 4.35, 251: 5.5, 500: 8.5}, 500, "W2")
        self.prices["W3"] = ShippingPrice({0: 0, 251: 0, 500: 2.22}, {0: 4.35, 251: 5.5, 500: 8.5}, 500, "W3")
        self.prices["T1"] = ShippingPrice({0: 0, 251: 0, 500: 1.45}, {0: 4.35, 251: 5.5, 500: 7.35}, 500, "T1")
        self.prices["NT1"] = ShippingPrice({0: 0, 251: 0, 500: 2.08}, {0: 4.35, 251: 5.5, 500: 8.5}, 500, "NT1")
    def checkCountry(self, country):
        country = country.lower().strip()
        if country == "australia":
            return True
    def calculate(self, zone, weight):
        if weight >= self.prices[zone].maxFixedPrice:
            weight = math.ceil(float(weight)/1000)*1000
        # postage gets taxed
        return self.prices[zone].getPrice(weight)*1.1
    def findZone(self, zone):
        for x in self.zones.keys():
            if self.zones[x].count(zone):
                return x
                break
if __name__ == "__main__":
    p = AustraliaPostDomestic()
    zone = p.findZone(2088)
    print zone
    price = p.calculate(zone, 250)
    print price
    