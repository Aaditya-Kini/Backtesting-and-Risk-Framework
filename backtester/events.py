class Event:
    pass

class MarketEvent(Event):
    def __init__(self, date, data):
        self.type = 'MARKET'
        self.date = date
        self.data = data 

class SignalEvent(Event):
    def __init__(self, date, ticker, direction):
        self.type = 'SIGNAL'
        self.date = date
        self.ticker = ticker
        self.direction = direction 

class OrderEvent(Event):
    def __init__(self, date, ticker, direction, quantity):
        self.type = 'ORDER'
        self.date = date
        self.ticker = ticker
        self.direction = direction
        self.quantity = quantity

class FillEvent(Event):
    def __init__(self, date, ticker, direction, quantity, price, commission):
        self.type = 'FILL'
        self.date = date
        self.ticker = ticker
        self.direction = direction
        self.quantity = quantity
        self.price = price
        self.commission = commission