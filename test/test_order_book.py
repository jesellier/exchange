# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 19:07:57 2021

@author: jesel
"""

from src.exchange import ExchangeOrderBook
from src.trading_book import TradingBook
   
import unittest
import logging



class TestOrderBook(unittest.TestCase):
    
    def setUp(self):
        
        logging.disable(logging.INFO)
        
        self.e = ExchangeOrderBook()
        trader1 = TradingBook("Trader1")
        trader1.setupWithExchange(self.e)
        
        trader2 = TradingBook("Trader2")
        trader2.setupWithExchange(self.e)

        self.trader1 = trader1
        self.trader2 = trader2
        
    def tearDown(self):
        logging.disable(logging.NOTSET)
    


    def test_simple_unfilled(self):
        orderId = self.trader1.orderAdd(self.e, "S", 50.34, 20)
        
        #must have received the order in the trader book
        self.assertTrue(orderId in self.trader1.book.keys())
        self.assertTrue(len(self.trader1.book) == 1)
        self.assertTrue(not self.trader1._pending_fill)
        
        order = self.trader1.book[orderId]
        self.assertTrue(order.side == 'S')
        self.assertTrue(order.price == 50.34)
        self.assertTrue(order.qty == 20)
        
    def test_two_unfilled(self):
        orderId1 = self.trader1.orderAdd(self.e, "S", 50.34, 20)
        orderId2 = self.trader1.orderAdd(self.e, "S", 48.34, 10)
        
        #must have received the order in the trader book
        self.assertTrue(orderId1 in self.trader1.book.keys())
        self.assertTrue(orderId2 in self.trader1.book.keys())
        self.assertTrue(len(self.trader1.book) == 2)
        self.assertTrue(not self.trader1._pending_fill)
        
    def test_filled_orders(self):
        orderId1 = self.trader1.orderAdd(self.e, "S", 50.34, 20)
        orderId2 = self.trader1.orderAdd(self.e, "S", 48.34, 10)
        
        #create matching order
        self.trader2.orderAdd(self.e, "B", 51.00, 15)
        
        #result eppected 
        #->trader2 fully filled
        #->trader1 remains 15 of order 1
        
        # trader2
        self.assertTrue(not self.trader2.book)
        self.assertTrue(not self.trader2._pending_fill)
        
        # trader1
        self.assertTrue(orderId1 in self.trader1.book.keys()) #orderId1 in portfolio
        self.assertTrue(orderId2 not in self.trader1.book.keys()) #orderId removed from portfolio
        self.assertTrue(len(self.trader1.book) == 1)
        self.assertTrue(not self.trader1._pending_fill)
        
        order = self.trader1.book[orderId1]
        self.assertTrue(order.side == 'S')
        self.assertTrue(order.price == 50.34)
        self.assertTrue(order.qty == 15)



if __name__ == '__main__':
    unittest.main()


  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    