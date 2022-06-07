# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 19:07:57 2021

@author: jesel
"""


class OrderAcknowledgementMsg:
    def __init__(self,  orderId, timestamp):
        self.orderId = orderId
        self.timestamp = timestamp
        
    def tostr(self):
        return "orderid:=" + str(self.orderId) + ",timestamp:=" + str(self.timestamp)
            
class FillConfirmationMsg:
    def __init__(self,  orderId, fillId, qty, timestamp):
        self.orderId = orderId
        self.fillId = fillId
        self.qty = qty
        self.timestamp = timestamp
    
    def tostr(self):
        return "orderid:=" + str(self.orderId) + ",fillId:=" + str(self.fillId) + \
               ",qty:=" + str(self.qty) + ",timestamp:=" + str(self.timestamp)


            
            



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    