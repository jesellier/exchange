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
        
        # SETUP the following default order book for testing:
        #------------------------------------------------
        # BUY                         SELL
        #-----------------            -------------------
        #Price      qty               Price        qty
        #------     ------            ------       ------
        #45.34      30                48.0         10
        #33.34      20                50.34        20
        #                             52.34        30 
        
        logging.disable(logging.INFO)

        self.e = ExchangeOrderBook()
        ibook = TradingBook("init_ID")
        ibook.setupWithExchange(self.e)
        
        
        #execute the default unmachted orders
        ibook.orderAdd(self.e,"S", 50.34, 20)
        ibook.orderAdd(self.e,"S", 48.0, 10)
        ibook.orderAdd(self.e,"S", 52.34, 30)
        ibook.orderAdd(self.e,"B", 33.34, 20)
        ibook.orderAdd(self.e,"B", 45.34, 30)

        self.init_buy_qty = [30, 20]
        self.init_buy_price = [45.34, 33.34]
        self.init_sell_qty = [10, 20, 30]
        self.init_sell_price = [48.0, 50.34, 52.34]
        self.ibook = ibook
        
    def tearDown(self):
        logging.disable(logging.NOTSET)


    def test_setup_buy(self):
        ### test the passing initial buy orders (output in DESC price order)
        self.assertTrue(self.e.buy_price_lst() == [45.34, 33.34])
        self.assertTrue(self.e.buy_qty_lst() == [30, 20])
        
    def test_setup_sell(self):
        ### test the passing of the initial sell orders (output in ASC price order)
        self.assertTrue(self.e.sell_price_lst() == [48.0, 50.34, 52.34])
        self.assertTrue(self.e.sell_qty_lst() == [10, 20, 30])
        

    #TEST SELL ORDERS
    def test_fill_sell_1(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "S", 44, 10)
        
        #BUY : Should match 10 from first 30@45.34 block
        self.assertTrue(self.e.buy_price_lst() == [45.34, 33.34])
        self.assertTrue(self.e.buy_qty_lst() == [20, 20])
        
        #SELL : unchanged
        self.assertTrue(self.e.sell_price_lst() == self.init_sell_price )
        self.assertTrue(self.e.sell_qty_lst() == self.init_sell_qty )

    
    def test_fill_sell_2(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "S", 30.0, 35)
        
        #BUY : Should match up to 5 of the second 30@33.34 block
        self.assertEqual(self.e.buy_price_lst(), [33.34] )
        self.assertEqual(self.e.buy_qty_lst(), [15] )
        
        #SELL : unchanged
        self.assertEqual(self.e.sell_price_lst(), self.init_sell_price )
        self.assertEqual(self.e.sell_qty_lst(), self.init_sell_qty )
        
        
    def test_fill_sell_3(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "S", 30.0, 50)
  
        #BUY : Should match the full blocks
        self.assertTrue(self.e.buy_price_lst() == [] )
        self.assertTrue(self.e.buy_qty_lst() == [] )
        
        #SELL : unchanged
        self.assertEqual(self.e.sell_price_lst(), self.init_sell_price )
        self.assertEqual(self.e.sell_qty_lst(), self.init_sell_qty )
        
        
    def test_unfilled_sell_1(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "S", 46.0, 10)

        #BUY : unchanged (no match)
        self.assertEqual(self.e.buy_price_lst(), self.init_buy_price )
        self.assertEqual(self.e.buy_qty_lst(), self.init_buy_qty )
        
        #SELL : should be inserted first
        self.assertTrue(self.e.sell_price_lst() == [46.0, 48.0, 50.34, 52.34])
        self.assertTrue(self.e.sell_qty_lst() == [10, 10, 20, 30])
        
    def test_unfilled_sell_2(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "S", 40.0, 35)

        #BUY : match the first 30@45.34 block only
        self.assertEqual(self.e.buy_price_lst(),  [33.34] )
        self.assertEqual(self.e.buy_qty_lst(), [20])
        
        #SELL : insert should be 5 qty sell order
        self.assertTrue(self.e.sell_price_lst() == [40.0, 48.0, 50.34, 52.34],)
        self.assertTrue(self.e.sell_qty_lst() == [5, 10, 20, 30])
        
        

    #TEST BUY ORDERS
    def test_fill_buy_1(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "B", 50.0, 5)
        
        #BUY : unchanged
        self.assertEqual(self.e.buy_price_lst(), self.init_buy_price )
        self.assertEqual(self.e.buy_qty_lst(), self.init_buy_qty )
        
        #SELL : Should match 5 from first 10@48 block
        self.assertTrue(self.e.sell_price_lst() == [48.0, 50.34, 52.34])
        self.assertTrue(self.e.sell_qty_lst() == [5, 20, 30])
        

    
    def test_fill_buy_2(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "B", 51.0, 17)
        
        #BUY : unchanged
        self.assertEqual(self.e.buy_price_lst(), self.init_buy_price )
        self.assertEqual(self.e.buy_qty_lst(), self.init_buy_qty )
        
        #SELL : Should match up to 7 of the second 20@50.34 block
        self.assertTrue(self.e.sell_price_lst() == [50.34, 52.34])
        self.assertTrue(self.e.sell_qty_lst() == [13, 30])
        
        
    def test_fill_buy_3(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "B", 53.0, 60)
        
        #BUY : unchanged
        self.assertEqual(self.e.buy_price_lst(), self.init_buy_price )
        self.assertEqual(self.e.buy_qty_lst(), self.init_buy_qty )
        
        #SELL : Should match the full blocks
        self.assertTrue(self.e.sell_price_lst() == [] )
        self.assertTrue(self.e.sell_qty_lst() == [] )

        
        
    def test_unfilled_buy_1(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "B", 44.0, 18)
        
        #BUY : should be inserted first
        self.assertTrue(self.e.buy_price_lst() == [45.34, 44.0, 33.34])
        self.assertTrue(self.e.buy_qty_lst() == [30, 18, 20])
        
        #SELL : unchanged (no match)
        self.assertTrue(self.e.sell_price_lst() == self.init_sell_price )
        self.assertTrue(self.e.sell_qty_lst() == self.init_sell_qty )
        
        
        
    def test_unfilled_buy_2(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "B", 51.0, 38)

        #BUY : insert should be 8 qty 
        self.assertTrue(self.e.buy_price_lst() == [51.0, 45.34, 33.34])
        self.assertTrue(self.e.buy_qty_lst() == [8, 30, 20])
        
        #SELL : match the first two block only (i.e. remain last)
        self.assertTrue(self.e.sell_price_lst() == [52.34],)
        self.assertTrue(self.e.sell_qty_lst() == [30])
        
        
        
    #TEST CANCEL ORDERS
    def test_cancel_1(self):
  
        orderId = list(self.ibook.book.keys())[2]
        #fetch the order 30@52.34 SELL block and cancel 10
        self.ibook.orderCancel(self.e, orderId, 10)
        
        #new SELL
        self.assertTrue(self.e.sell_price_lst() == [48.0, 50.34, 52.34])
        self.assertTrue(self.e.sell_qty_lst() == [10, 20, 20])
        

    def test_cancel_2(self):
  
        orderId = list(self.ibook.book.keys())[3]
        #fetch the order 20@33.34 BUY block and cancel all
        self.ibook.orderCancel(self.e, orderId, 20)
        
        #new BUY
        self.assertTrue(self.e.buy_price_lst() == [45.34])
        self.assertTrue(self.e.buy_qty_lst() == [30])
        
        
        
        
    #TEST ORDER PRIORITY
    def test_priority_buy(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "B", 45.34, 10)

        #new BUY
        self.assertTrue(self.e.buy_price_lst() == [45.34, 45.34, 33.34])
        self.assertTrue(self.e.buy_qty_lst() == [30, 10, 20])
        
    #TEST ORDER PRIORITY
    def test_priority_sell(self):
        dbook = TradingBook("dummyID")
        dbook.setupWithExchange(self.e)
        dbook.orderAdd(self.e, "S", 50.34, 25)

        #new BUY
        self.assertTrue(self.e.sell_price_lst() == [48.0, 50.34, 50.34, 52.34])
        self.assertTrue(self.e.sell_qty_lst() == [10, 20, 25, 30])

        
        
 


if __name__ == '__main__':
    unittest.main()


  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    