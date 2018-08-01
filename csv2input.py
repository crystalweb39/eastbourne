'''
@author: chaol
'''

import csv as _csv
import sys

class csv2input:
    def __init__(self,csv, type='product'):
        self.title = []
        self.data = []
        self.error = ''
        if type == 'product':
            temp = self.readcsv(csv)
        
        else:
            temp = self.readimage(csv)
        print temp
        if len(temp) > 1:
            
            self.title = temp[0]
            self.data = temp[1:]
        
    def readimage(self,csv):
        temp = []
        spamReader = _csv.reader(open(csv,'rb'),delimiter=',')
        for i,row in enumerate(spamReader):
            temp.append(row)
        return temp
        
    def checkImageType(self,list):
        for name in list:
            names = name.strip().split('.')
            if names and len(names) ==2 and len(names[1]) <5:
                return True
        return False
            
            
    
    def readcsv(self,csv):
        temp = []
        v = ''
        spamReader = _csv.reader(open(csv,'rb'),delimiter=',')
        
        for i,row in enumerate(spamReader):
            if i == 0:
                try:
                    v = self.reorder(row, 0, 'status')
                except:
                    break
            else:
                if v==0:
                    self.addColumn(row,0,"Available")
                else:
                    self.swapColumn(row,v,0)
                
            temp.append(row)
        
        return temp

    def addColumn(self,list,index,value):
        list.insert(index,value)

    def swapColumn(self,list,init,dest):
        
        value = list[init]
        list.pop(init)
        
        list.insert(dest,value)
        
        
    def reorder(self,list,dest,value):
        temp = 0
        if list.count(value) == 0:
           
            self.addColumn(list,dest,value)
            
        elif list.count(value) == 1:
            temp = list.index(value)
            
            self.swapColumn(list,list.index(value),dest)
            
        else:
            print "Error: line 1 has more than 1 '" + value+ "'"
            sys.exit(1)
        return temp
        
#input = csv2input('/home/chaol/workspace/eastbourneart/images.csv',type='image')
#print input.title
#print input.data
