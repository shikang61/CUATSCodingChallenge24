from AlgorithmImports import *

class EMACrossoverTrailingStopAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2010, 1, 1)    #Set Start Date
        self.SetEndDate(2021, 11, 27)    #Set End Date
        self.SetCash(100000)             #Inital Cash set to USD100000
        self.SetWarmUp(200)              #Provide warm-up 

        # Define self.symbol and self.altsymbol for later function call (as we try various pairs of assets)
        self.symbol = self.AddEquity("SPY").Symbol 
        self.altsymbol = self.AddEquity("SHY").Symbol
        # Define EMAs for self.symbol
        self.ema_fast = self.EMA(self.symbol, 10, Resolution.Hour)
        self.ema_slow = self.EMA(self.symbol, 50, Resolution.Hour)

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

        # Check for EMA crossover
        tolerance=0.00015
        if self.ema_fast.Current.Value > self.ema_slow.Current.Value* (1 + tolerance) and self.Portfolio[self.symbol].Quantity == 0:
            # Buy signal
            self.SetHoldings(self.symbol, 1.0)
            self.Liquidate(self.altsymbol)
            self.max_price = self.Securities[self.symbol].Price

        # Check for trailing stop loss
        elif (self.Securities[self.symbol].Close < self.max_price * self.trailing_stop_percent) and self.Portfolio[self.symbol].Quantity > 0:
            # Sell signal
            self.Liquidate(self.symbol)
            self.SetHoldings(self.altsymbol, 1.0)

        # Invest in self.altsymbol if the self.symbol does not meet the buy criterion on the first day
        if not self.Portfolio.Invested:
            self.SetHoldings(self.altsymbol, 1.0)

        # Update to current time
        self.previous = self.Time

    def OnEndOfDay(self):
        # Update max price at the end of each day
        if self.Portfolio.Invested:
            self.max_price = max(self.max_price, self.Securities[self.symbol].Close)
