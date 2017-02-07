########################################################################################################
#
#  Strategies: Market Strategies
#
#  Author: Anthony Rodriguez
#  Date: December 2016
#
########################################################################################################

from datetime import datetime
from matplotlib.dates import date2num
import pandas as pd

def EvaluateStrat(mktData, strat, start, end):
  commissionFee = 5.0
  strat.cashBaseline = 0.0
  strat.commissionOverhead = 0.0
  strat.cash = [0]*len(mktData)
  strat.assets = [0]*len(mktData)
  strat.equity = [0]*len(mktData)
  prevPayDate = mktData.Date[start]
  strat.cash[start] = strat.biWeeklyCashFlow
  for i in range(start, end+1):
    #Asset appreciation/depreciation
    if i>0:
      pctChange = (mktData.Close[i] - mktData.Close[i-1])/mktData.Close[i-1]
      strat.assets[i] = strat.assets[i-1] + strat.assets[i-1]*pctChange
      strat.cash[i] = strat.cash[i-1]
    #Handle incoming cashflow
    if (mktData.Date[i] - prevPayDate).days >= 14:
      prevPayDate = mktData.Date[i]
      strat.cash[i] = strat.cash[i] + strat.biWeeklyCashFlow
      strat.cashBaseline = strat.cashBaseline + strat.biWeeklyCashFlow
    #Handle sell command
    if strat.sellCmds[i] > 0.0:
      profitsTaken = strat.assets[i]*strat.sellCmds[i]
      strat.assets[i] = strat.assets[i] - profitsTaken
      strat.cash[i] = strat.cash[i] + profitsTaken
      strat.commissionOverhead = strat.commissionOverhead + commissionFee
      strat.cash[i] = strat.cash[i] - 5.0
      if strat.cash[i] < 0.0:
        print('WARNING: Strategy resulted in not enough cash to cover commissions (sale)')
    #Handle buy command
    if strat.buyCmds[i] > 0.0:
      strat.cash[i] = strat.cash[i] - commissionFee
      strat.commissionOverhead = strat.commissionOverhead + commissionFee
      buyAmount = strat.cash[i] * strat.buyCmds[i]
      strat.assets[i] = strat.assets[i] + buyAmount
      strat.cash[i] = strat.cash[i] - buyAmount
      if strat.cash[i] < 0.0:
        print('WARNING: Strategy resulted in not enough cash to cover commissions (buy)')
    strat.equity[i] = strat.cash[i] + strat.assets[i]
  #PostProcessing
  strat.totalEquity = strat.equity[end]
  strat.totalAppreciation = (strat.totalEquity - strat.cashBaseline) / strat.cashBaseline * 100.0 

class Strategy(object):
  def __init__(self):
    self.buyCmds = []
    self.sellCmds = []
    self.label = 'ERR'
    self.biWeeklyCashFlow = 800.0
    self.cash = []
    self.assets = []
    self.commissionOverhead = 0.0
    self.cashBaseline = 0.0
    self.totalEquity = 0.0
    self.equity = []
    self.totalAppreciation = 0.0

  def setData(self, bollingerLow, bollingerHigh, macdRed, macdBlack, macdHist):
    self.bollingerLow = bollingerLow
    self.bollingerHigh = bollingerHigh
    self.macdRed = macdRed
    self.macdBlack = macdBlack
    self.macdHist = macdHist
    self.dataInit = True

  def RunStrat(self, mktData):
    print('ERR')

class NoStrategy(Strategy):
  def __init__(self):
    super(NoStrategy, self).__init__()
    self.label='No Strategy'
    self.bollingerLow = []
    self.bollingerHigh = []
    self.macdRed = []
    self.macdBlack = []
    self.macdHist = []
    self.dataInit = False

  def setData(self, bollingerLow, bollingerHigh, macdRed, macdBlack, macdHist):
    Strategy.setData(self, bollingerLow, bollingerHigh, macdRed, macdBlack, macdHist)

  def RunStrat(self, mktData, start, end):
    self.buyCmds = [0]*len(mktData)
    self.sellCmds = [0]*len(mktData)


class PriceAveraging(Strategy):
  def __init__(self):
    super(PriceAveraging, self).__init__()
    self.label='Price Averaging'

  def setData(self, bollingerLow, bollingerHigh, macdRed, macdBlack, macdHist):
    Strategy.setData(self, bollingerLow, bollingerHigh, macdRed, macdBlack, macdHist)

  def RunStrat(self, mktData, start, end):
    self.buyCmds = [0]*len(mktData)
    self.sellCmds = [0]*len(mktData)
    self.buyCmds[start] = 1.0
    prevBuyDate = mktData.Date[start]
    for i in range(start, end+1): 
      if (mktData.Date[i] - prevBuyDate).days >= 14:
        self.buyCmds[i] = 1.0
        prevBuyDate = mktData.Date[i]
        

class Signal(Strategy):
  def __init__(self):
    super(Signal,self).__init__()
    self.label='Signals'

  def setData(self, bollingerLow, bollingerHigh, macdRed, macdBlack, macdHist):
    Strategy.setData(self, bollingerLow, bollingerHigh, macdRed, macdBlack, macdHist)

  def RunStrat(self, mktData, start, end):

    #ema180 = pd.ewma(mktData.Close, span=180)
    #ema365 = pd.ewma(mktData.Close, span=365)

    self.buyCmds = [0]*len(mktData)
    self.sellCmds = [0]*len(mktData)
    nothingToSell = True
    if self.dataInit is False:
      print( 'Could not run Signal strat: data not initialized' )
      return
    prevBuyDate = mktData.Date[start]
    for i in range(start+1,end+1):
      #Buy signal
      if (    self.macdBlack[i] < self.macdRed[i] 
          and self.macdRed[i-1] < 0.0  
          and self.macdBlack[i-1] < 0.0
          and mktData.Close[i] < self.bollingerLow[i]
          and (mktData.Date[i] - prevBuyDate).days >= 14): 
        self.buyCmds[i+1] = 1.0
        prevBuyDate = mktData.Date[i]
        nothingToSell = False
      elif ( not nothingToSell and mktData.Close[i] < self.bollingerHigh[i] and mktData.Close[i-1] >= self.bollingerHigh[i-1]):
        self.sellCmds[i+1] = 1.0
        nothingToSell = True















