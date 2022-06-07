# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 19:07:57 2021

@author: jesel
"""

import time
import warnings


class TradingBook :
    
    class OrderStruct :
        def __init__(self,  orderId, side, price, qty, timestamp):
            self.orderId = orderId
            self.side = side
            self.price = price
            self.qty = qty
            self.timestamp = timestamp


    def __init__(self, traderID, limit_per_sec = 100):
        self.id = traderID
        self.book = {}
        self._pending_fill = {}
        
        #limt mechanism
        # use time.time() returns the time as a floating point number expressed in seconds since the epoch, in UTC
        self.last_time = 0     
        self.limit_per_sec = limit_per_sec
        self.count = 0
        
    def setupWithExchange(self, exchange):
        exchange.setupConnection(self)
        
    def _is_below_limit(self, timestamp):
        if timestamp - self.last_time > 1 : 
            self.count = 1
            self.last_time = timestamp
            return True
        else :
            if self.count + 1 > self.limit_per_sec :
                return False
        self.count +=1
        return True
    
    
        
    def orderAdd(self, exchange, side, price, qty):
        timestamp = time.time()

        if not self._is_below_limit(timestamp) :
            warnings.warn("number of order excedeed " + str(self.limit_per_sec))
            return None
            
        msg = exchange.executeAdd(self.id, side, price, qty, timestamp)
        orderId = msg.orderId
        ## insert order in the book
        self.book[orderId] = TradingBook.OrderStruct(orderId, side, price, qty, msg.timestamp)
        ## process pending fill acknoledgement if any
        if orderId in self._pending_fill.keys() :
            pending = self._pending_fill[orderId]
            self.accept(pending)
            del self._pending_fill[orderId] 
                
        return orderId

        
        
    def orderCancel(self, exchange, orderId, qty):
         timestamp = time.time()
        
         if orderId not in self.book.keys() :
            raise ValueError("order " + orderId + "does not exists in 'book'")

         if not self._is_below_limit(timestamp) :
            warnings.warn("number of order excedeed " + str(self.limit_per_sec))
            return None
        
         if exchange.executeCancel(self.id, orderId, qty, timestamp):
             order = self.book[orderId]
             new_qty = max(order.qty - qty, 0)
                
             if new_qty == 0 :
                 del self.book[orderId]
             else: 
                 order.qty = new_qty


    def accept(self, msg) :
        #process the asynchroneous fill msg
        orderId = msg.orderId
        
        #if order not in book put it in a buffer (waiting for orderAckowledgement)
        if orderId not in self.book.keys() :
            self._pending_fill[orderId] = msg
            return
        #else update the trading book
        order = self.book[orderId]
        order.qty -= msg.qty
        if order.qty == 0 :
            del self.book[orderId]



    