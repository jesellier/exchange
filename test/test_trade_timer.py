# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 19:07:57 2021

@author: jesel
"""

from src.trading_book import TradingBook
import time
import unittest


class MockedTradingBook(TradingBook):
    
    def __init__(self, traderId, limit_per_sec = 100):
        super().__init__(traderId, limit_per_sec)
        
        
    def mockedOrder(self):
        timestamp = time.time()
        tag = 1
        
        if not self._is_below_limit(timestamp) :
            tag = 0

        return tag
        
 

class TestBookTimer(unittest.TestCase):
           
    def test_timer(self):
        trader = MockedTradingBook("dummy", limit_per_sec = 5)
        t_end = time.time() + 2
        r = []
        while time.time() < t_end:
            r.append(trader.mockedOrder())

        self.assertIn(sum(r), [9,10,11])

                        

if __name__ == '__main__':
    unittest.main()


  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    