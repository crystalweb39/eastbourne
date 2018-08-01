'''
Created on 25/09/2009

@author: telliott
'''
import math
class ShippingPrice:
    def __init__(self, weights, article, maxfixed, zone):
        self.weightprice = weights
        self.articleprice = article
        self.maxFixedPrice = maxfixed
        self.zone = zone
    def getPrice(self, weight):
        """
        Calculate a total price based on zone, per article and perkg
        """
        values = self.weightprice.keys()
        values.sort()
        values.reverse()
        wp = 0
        for x in values:
            if weight >= x:
                wp = float(self.weightprice[x])
                # TODO we should probably run this in a separate loop incase the categories diverge
                ap = float(self.articleprice[x])
                break
        if self.maxFixedPrice and weight <= self.maxFixedPrice:
            return round(float(wp) + float(ap), 2)
        else:
            return round(float((float(weight)/1000) * wp)+float(ap), 2)