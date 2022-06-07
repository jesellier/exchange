# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 19:07:57 2021

@author: jesel
"""


import time
import uuid
from pyllist import dllist, dllistnode

from src.msg import OrderAcknowledgementMsg, FillConfirmationMsg
from src.configs import getLogger

logger = getLogger(__name__)



    
class ExchangeOrderBook :
    

    class ListNode :
        def __init__(self,  orderId, price, qty, timestamp):
            self.orderId = orderId
            self.price = price
            self.qty = qty
            self.timestamp = timestamp
 
        def tostr(self):
            return "orderid:=" + str(self.orderId) + ",price:=" + str(self.price) \
                   + ",qty:=" + str(self.qty) + ",timestamp:=" + str(self.timestamp) 

        
    class OrderInfos :
        def __init__(self, clientId, side):
            self.clientId = clientId
            self.side = side

    class SideParser :
        def __init__(self, orderSideStr) :
            if orderSideStr in ["B", "BUY", "buy", "b"]:
                self.insert_tag = "buy"  #tag for insert
                self.fill_tag = "sell" #tag for fill
            elif orderSideStr in ["S", "SELL", "sell", "s"]:
                self.insert_tag = "sell"
                self.fill_tag = "buy"
            else:
                raise ValueError("order str type not recognize")


    def __init__(self):
        self.mapOrders = {}   ## map: key:=tradeID, value:= orderInfos
        self.mapClients = {}   ## map: key:=clientID, value:= clientObj
        self.buy = dllist()
        self.sell = dllist()
        

    def setupConnection(self, client):
        self.mapClients[client.id] = client
        

    def executeAdd(self, clientId, side, price, qty, timestamp):
        
        if clientId not in self.mapClients.keys() :
            raise ValueError("clientID must be stored")

        orderId = self.__new_order_id()
        parser = ExchangeOrderBook.SideParser(side)
        order = ExchangeOrderBook.ListNode(orderId, price, qty, timestamp)
        logger.info("receive:OrderAdd~" + "clientid:=" + str(clientId) +"," +  order.tostr())
        
        #try to fill the order
        filled = self.__fillOrder(order, block = parser.fill_tag)
        

        #insert unfilled order
        if filled != order.qty  :
            order.qty -= filled
            self.__insertOrder(order, block = parser.insert_tag)
        
        #close with msg
        execution_time = time.time()
        self.mapOrders[orderId] = ExchangeOrderBook.OrderInfos(clientId, parser.insert_tag)

        if filled > 0 :  
            self.__send_fill_msg(orderId, qty, execution_time, clientId)
            
        msg = OrderAcknowledgementMsg(orderId, execution_time)
        logger.info("send:OrderAcknowledgementMsg~" + "clientid:=" + str(clientId) +"," +  msg.tostr())
            
        return msg
    
    
    def executeCancel(self, clientId, orderId, cancel_qty, timestamp):
        
        if clientId not in self.mapClients.keys() :
            raise ValueError("clientID must be stored")
        
        infos = self.mapOrders[orderId]
        self.__modifyOrder(orderId, cancel_qty, infos.side)
        logger.info("receive:OrderCancel~" + "clientid:=" + str(clientId) +",orderid:=" + str(orderId)  \
                    + ",qty:=" + str(cancel_qty) + ",timestamp:=" + str(timestamp))
        
        cancelingConfirmation = True
        return cancelingConfirmation



    def __new_order_id(self):
        return uuid.uuid1()


    def __send_fill_msg(self, orderId, qty, timestamp, clientId = None):
        #order fill confirmation message
        fillId = self.__new_order_id()
        if clientId is None :
            clientId = self.mapOrders[orderId].clientId
              
        msg = FillConfirmationMsg(orderId, fillId, qty, timestamp)
        logger.info("send:FillMsg~" + "clientid:=" + str(clientId) +"," +  msg.tostr())
        self.mapClients[clientId].accept(msg)    
        
      
    def __insertOrder(self, order, block = "sell"):
        
        lst = getattr(self, block)
        
        flip = 1.0
        if block == "buy" :
            flip = -1.0

        if order.qty == 0 :
            return
        
        new_node = dllistnode(order)
        if lst.size == 0 :
            lst.append(new_node)
            return

        for node in lst.iternodes():  
            if flip * order.price < flip * node.value.price:
                lst.insert(new_node, node) 
                return
            
        lst.insert(new_node, after = node) 

        
    
    def __modifyOrder(self, orderId, qty,  block = 'sell'):

        lst= getattr(self, block)
        
        for node in lst.iternodes():
            if node.value.orderId == orderId:
                break
            
        new_qty = max(node.value.qty - qty, 0)

        if new_qty > 0 :
            node.value.qty = new_qty
        else :
            lst.remove(node)       
        
            


    def __fillOrder(self, order, block = "sell"):
        
        lst = getattr(self, block)
        running_sum = 0
        filled = 0
        
        flip = 1.0
        if block == "buy" :
            flip = -1.0
        
        execution_time = time.time()
        node = lst.first

        for i in range(lst.size) :
             #break for price condition
             if flip * node.value.price > flip * order.price :
                 filled = running_sum
                 return filled
             #break for being fully filled
             if running_sum + node.value.qty > order.qty :
                 filled = order.qty 
                 delta = order.qty - running_sum
                 node.value.qty  -=  delta
                 self.__send_fill_msg(node.value.orderId, delta, execution_time)
                 return filled

             running_sum += node.value.qty
             filled_node = node
             node = node.next
             
             self.__send_fill_msg(filled_node.value.orderId, filled_node.value.qty, execution_time)
             lst.remove(filled_node)
             
        filled = running_sum
        return filled
    
    

    def sell_qty_lst(self):
        lst = []
        for node in self.sell.iternodes():  
            lst.append(node.value.qty)
        return lst
    
    def sell_price_lst(self):
        lst = []
        for node in self.sell.iternodes():  
            lst.append(node.value.price)
        return lst
    
    def buy_qty_lst(self):
        lst = []
        for node in self.buy.iternodes():  
            lst.append(node.value.qty)
        return lst
    
    def buy_price_lst(self):
        lst = []
        for node in self.buy.iternodes():  
            lst.append(node.value.price)
        return lst
        

    def __repr__(self):
        rep = "SELL: "
        sprice = []
        sqty = []
        for node in self.sell.iternodes():  
            sprice.append(node.value.price)
            sqty.append(node.value.qty)
        rep += "price=:" + str(sprice) + ", "
        rep += "qty=:" + str(sqty)
        
        rep += "\n" + "BUY: "
        bprice = []
        bqty = []
        for node in self.buy.iternodes():  
            bprice.append(node.value.price)
            bqty.append(node.value.qty)
        rep += "price=:" + str(bprice) + ", "
        rep += "qty=:" + str(bqty)
        
        return rep
    

if __name__ == "__main__" :
    
    from src.trading_book import TradingBook
    
    e = ExchangeOrderBook()
    
    t1 = TradingBook("Trader1")
    t1.setupWithExchange(e)
    
    t2 = TradingBook("Trader2")
    t2.setupWithExchange(e)
    
    t2.orderAdd(e, "B", 48.34, 10)
    t2.orderAdd(e, "B", 50.34, 20)
    t2.orderAdd(e, "B", 51.34, 10)
    #t1.orderAdd(e, "B", 51.00, 5)
    
    #orderId = list(t2.book.keys())[0]
    #order = t2.book[orderId]
    #t2.orderCancel(e, orderId, 5)

    print(e)




    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    