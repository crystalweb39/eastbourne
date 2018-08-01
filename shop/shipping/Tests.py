'''
Created on 25/09/2009

@author: telliott
'''
import unittest

from AustraliaPostDomestic import *
from AustraliaPostInternational import *

class Test(unittest.TestCase):
    def testAustralianDomesticShippingPrices(self):
        p = AustraliaPostDomestic()
        #
        # lets check Mosman
        #
        zone = p.findZone(2088)
        self.assertEqual("N1", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.1, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(5.8, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(5.8, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(5.8, price)
        #
        # lets check TWEED HEADS
        #
        zone = p.findZone(2485)
        self.assertEqual("N2", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(7.81, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(9.25, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(9.61, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(14.65, price)
        #
        # lets check Melbourne
        #
        zone = p.findZone(3000)
        self.assertEqual("V1", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(7.84, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(9.8, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(10.29, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(17.15, price)
        #
        # lets check BIRREGURRA, vic
        #
        zone = p.findZone(3242)
        self.assertEqual("V2", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(9.16, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(11.8, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(12.46, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(21.7, price)
        #
        # lets check COOLANGATTA
        #
        zone = p.findZone(4225)
        self.assertEqual("Q1", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(7.84, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(9.8, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(10.29, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(17.15, price)
        #
        # lets check MOUNT MELLUM, QLD
        #
        zone = p.findZone(4550)
        self.assertEqual("Q2", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(9.33, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(12.65, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(13.48, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(25.1, price)
        #
        # lets check ROCKHAMPTON, QLD
        #
        zone = p.findZone(4700)
        self.assertEqual("Q3", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(9.61, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(14.05, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(15.16, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(30.7, price)
        #
        # lets check ADELAIDE, SA
        #
        zone = p.findZone(5800)
        self.assertEqual("S1", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(7.92, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(10.2, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(10.77, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(18.75, price)
        #
        # lets check TOTNESS, SA
        #
        zone = p.findZone(5250)
        self.assertEqual("S2", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(9.37, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(12.85, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(13.72, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(25.9, price)
        #
        # lets check PERTH, WA
        #
        zone = p.findZone(6000)
        self.assertEqual("W1", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(8.79, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(14.55, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(15.99, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(36.15, price)
        #
        # lets check NANGA BROOK, WA
        #
        zone = p.findZone(6215)
        self.assertEqual("W2", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(10.3, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(17.5, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(19.3, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(44.5, price)
        #
        # lets check CANE, WA
        #
        zone = p.findZone(6710)
        self.assertEqual("W3", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(10.72, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(19.6, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(21.82, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(52.9, price)
        #
        # lets check HOBART, TAS
        #
        zone = p.findZone(7000)
        self.assertEqual("T1", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(8.8, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(14.6, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(16.05, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(36.35, price)
        #
        # lets check DARWIN, NT
        #
        zone = p.findZone(800)
        self.assertEqual("NT1", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(4.35, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(4.35, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(5.5, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(10.58, price)
        # send 5000 grams
        price = p.calculate(zone, 5000)
        self.assertEqual(18.9, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(20.98, price)
        # send 5000 grams
        price = p.calculate(zone, 20000)
        self.assertEqual(50.1, price)
        
    def testAustralianInternationalShippingPrices(self):
        p = AustraliaPostInternational()
        #
        # lets check NZ
        #
        zone = p.findZone("New Zealand")
        self.assertEqual("A", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(2.85, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(6.21, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(6.23, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(9.72, price)
        # send 5000 grams
        price = p.calculate(zone, 2000)
        self.assertEqual(30.73, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(52.79, price)
        # send 20kg
        price = p.calculate(zone, 20000)
        self.assertEqual(162.45, price)
        #
        # lets check China
        #
        zone = p.findZone("China")
        self.assertEqual("B", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(2.89, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(7.3, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(7.31, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(11.88, price)
        # send 5000 grams
        price = p.calculate(zone, 2000)
        self.assertEqual(39.39, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(67.37, price)
        # send 20kg
        price = p.calculate(zone, 20000)
        self.assertEqual(207.58, price)
        #
        # lets check Canada
        #
        zone = p.findZone("Canada")
        self.assertEqual("C", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(2.94, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(8.38, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(8.4, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(14.04, price)
        # send 5000 grams
        price = p.calculate(zone, 2000)
        self.assertEqual(48.03, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(88.74, price)
        # send 20kg
        price = p.calculate(zone, 20000)
        self.assertEqual(291.23, price)
        #
        # lets check Norway
        #
        zone = p.findZone("Norway")
        self.assertEqual("D", zone)
        # send 10 grams
        price = p.calculate(zone, 10)
        self.assertEqual(3.55, price)
        # send 250 grams
        price = p.calculate(zone, 250)
        self.assertEqual(10.05, price)
        # send 251 grams
        price = p.calculate(zone, 251)
        self.assertEqual(10.08, price)
        # send 500 grams
        price = p.calculate(zone, 500)
        self.assertEqual(16.82, price)
        # send 5000 grams
        price = p.calculate(zone, 2000)
        self.assertEqual(57.44, price)
        # send 5000 grams
        price = p.calculate(zone, 5100)
        self.assertEqual(112.01, price)
        # send 20kg
        price = p.calculate(zone, 20000)
        self.assertEqual(380.95, price)
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testAustralianDomesticShippingPrices']
    unittest.main()
    


