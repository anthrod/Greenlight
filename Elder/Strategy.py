from matplotlib import pyplot as plt

class Strategy(object):
  def __init__(self, verbose=False):
    self.verbose = verbose

  def dailyUpdate(self, cash, income, security, day, evaluator):
    nothing = True



class CostAveragingStrategy(Strategy):
  def __init__(self, verbose=False):
    super(CostAveragingStrategy,self).__init__(verbose=verbose)

  def dailyUpdate(self, cash, income, security, day, evaluator):
    amtAvailable = cash.balance - security.commissionCost
    if (amtAvailable > 0):
      cash.buy(security, amtAvailable, evaluator, day)


class SignalStrategy(Strategy):
  def __init__(self, verbose=False):
    super(SignalStrategy,self).__init__(verbose=verbose)
    self.verbose = verbose
    self.mktState = 'Bear'
    self.bollingerState = 'Neutral'
    self.ema180state = 'Above'
    self.highestBuy = 0
    self.cashInvested = 0

  def dailyUpdate(self, cash, income, security, day, evaluator):
    longEMA  = security.getIndicator( indicatorType = 'EMA', movingAvgDays = 360 )
    shortEMA = security.getIndicator( indicatorType = 'EMA', movingAvgDays = 180 )
    macd     = security.getIndicator( indicatorType = 'MACD' )
    bollinger = security.getIndicator( indicatorType = 'Bollinger' ) 

    #State transitions
    prevBollingerState = self.bollingerState
    if (shortEMA.data.Avg[day] > longEMA.data.Avg[day] and self.mktState == 'Bear'):
      self.mktState = 'Bull'
    elif (shortEMA.data.Avg[day] <= longEMA.data.Avg[day] and self.mktState == 'Bull'):
      self.mktState = 'Bear'
    if security.dailyHistory['Adj Close'][day] < bollinger.data['Low'][day]: 
      self.bollingerState = 'Below'
    elif security.dailyHistory['Adj Close'][day] > bollinger.data['High'][day]:
      self.bollingerState = 'Above'
    else:
      self.bollingerState = 'Neutral'
    if security.dailyHistory['Adj Close'][day] < shortEMA.data.Avg[day]: 
      self.ema180state = 'Below'
    else: 
      self.ema180state = 'Above'

    #Strategy

    #Always buy if MACD below -40
    if macd.data['Black'][day] < -20.0 and macd.data['Red'][day] < -20.0:
      amtAvailable = cash.balance - security.commissionCost
      if (amtAvailable > 0):
        cash.buy(security, amtAvailable, evaluator, day)
        self.cashInvested = self.cashInvested + amtAvailable 
        self.highestBuy = max(self.highestBuy, security.dailyHistory['Adj Close'][day])
     
    if self.bollingerState=='Below' and self.ema180state=='Below':
      if self.mktState=='Bull':# or (macd.data.Black[day] < 40.0 and macd.data.Red[day] < 40.0):
        amtAvailable = cash.balance - security.commissionCost
        if (amtAvailable > 0):
          cash.buy(security, amtAvailable, evaluator, day)          
          self.cashInvested = self.cashInvested + amtAvailable     
          self.highestBuy = max(self.highestBuy, security.dailyHistory['Adj Close'][day])

    elif self.bollingerState=='Neutral' and prevBollingerState=='Above':
      amtInvested = security.investedAmount
      amtInvested = amtInvested * 7.0/8.0
      if amtInvested > self.cashInvested + security.commissionCost and security.dailyHistory['Adj Close'][day] > self.highestBuy:
        cash.sell(security, amtInvested, evaluator, day)
        self.cashInvested = max(0, self.cashInvested - amtInvested - security.commissionCost)        
        self.highestBuy = 0.0






