# example algorithm for the CUATS coding challenge
# this is a very simple EMA strategy that you will have seen before in our workshops
# you can build your algorithm out from this example, but make sure to check template.py to see the parameters you can/cannot change
from datetime import timedelta
from QuantConnect.Securities.Equity import Equity
from AlgorithmImports import *

class EMACrossoverTrailingStopAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2010, 1, 1)    #Set Start Date
        self.SetEndDate(2021, 11, 27)    #Set End Date
        self.SetCash(100000)             #Set Strategy Cash
        self.SetWarmUp(200)

        # Define the stock
        self.symbol = self.AddEquity("SPY").Symbol

        # Define EMAs
        self.ema_fast = self.EMA(self.symbol, 20, Resolution.Daily)
        self.ema_slow = self.EMA(self.symbol, 100,Resolution.Daily)

        # Define trailing stop loss
        self.trailing_stop_percent = 0.9
        self.max_price = 0
        self.previous = None

    def OnData(self, slice):
        # Update EMAs
        if self.IsWarmingUp:
            return

        if self.previous is not None and self.previous.date() == self.Time.date():
            return 

        self.ema_fast.Update(self.Time, self.Securities[self.symbol].Close)
        self.ema_slow.Update(self.Time, self.Securities[self.symbol].Close)

        # Check for crossover
        tolerance=0.00015
        if self.ema_fast.Current.Value > self.ema_slow.Current.Value* (1 + tolerance) and not self.Portfolio.Invested:
            # Buy signal
            self.SetHoldings(self.symbol, 1.0)
            self.max_price = self.Securities[self.symbol].Price

        # Check for crossover in the opposite direction or trailing stop loss
        #self.ema_fast.Current.Value < self.ema_slow.Current.Value or
        elif (self.Securities[self.symbol].Close < self.max_price * self.trailing_stop_percent) and self.Portfolio.Invested:
            # Sell signal
            self.Liquidate(self.symbol)
        
        self.previous = self.Time

    def OnEndOfDay(self):
        # Update max price at the end of each day
        if self.Portfolio.Invested:
            self.max_price = max(self.max_price, self.Securities[self.symbol].Close)
