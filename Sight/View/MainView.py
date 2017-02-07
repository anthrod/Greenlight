########################################################################################################
#
#  MainView: Main Window for GreenLight
#
#  Author: Anthony Rodriguez
#  Date: December 2016
#
########################################################################################################
from Sight.Control import plotlines as pl
from Sight.Model import Strategies
from Sight.View import PlotOverlay as po

import os
import time
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.finance
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime as dt
from matplotlib.dates import num2date
from matplotlib.dates import date2num
from pandas.io.data import DataReader
from datetime import datetime
from matplotlib.finance import *

from matplotlib import rcParams
from matplotlib.ticker import  IndexLocator, FuncFormatter, NullFormatter, MultipleLocator
from matplotlib.dates import IndexDateFormatter, date2num
from matplotlib.finance import  volume_overlay, index_bar
from pylab import *

class MainView(object):
  def __init__(self):   
    self.mainData = []
    self.mainDataSymbol = 'NONE'
    self.overlayList = [] 
    self.mktStrategy = Strategies.NoStrategy()
    self.enableBollinger = False
    self.bollingerSig = 1
    self.bollingerLength = 45
    self.bollingerLow = []
    self.bollingerHigh = []
    self.MACDlong = 26
    self.MACDshort = 12
    self.MACDsigLen = 9
    self.MACD = []
    self.MACDsignal = []
    self.MACDindicator = []
    self.dateArry = []
    self.startDay = 0
    self.startMonth = 0
    self.startYear = 0
    self.endDay = 99
    self.endMonth = 99
    self.endYear = 3000
    self.startIdx = 0
    self.endIdx = 0
    self.rsi = []
    self.mfi = []
    self.rsiLen = 10

  def setMainData(self, dataFrame, symbol):
    self.mainData = dataFrame
    self.mainDataSymbol = symbol
    self.overlayList = []

    #MACD
    emaSpan = (self.MACDshort-1)/2
    emaShort = pd.ewma(self.mainData.Close, span=emaSpan)
    emaSpan = (self.MACDlong-1)/2
    emaLong = pd.ewma(self.mainData.Close, span=emaSpan)
    self.MACD = emaShort-emaLong
    emaSpan = (self.MACDsigLen-1)/2
    self.MACDsignal = pd.ewma(self.MACD, span=emaSpan)
    self.MACDindicator = self.MACD-self.MACDsignal

    self.rsi = [50]*len(self.mainData)
    self.mfi = [50]*len(self.mainData)
    avgGain = [0]*len(self.mainData)
    avgLoss = [0]*len(self.mainData)
    moneyFlow = [0]*len(self.mainData)
    rs = 0
    #RSI/MFI
    for i in range(1,self.rsiLen):
      moneyFlow[i] = self.mainData.Volume[i]*(self.mainData.High[i] + self.mainData.Low[i] + self.mainData.Close[i])/3    
    for i in range(self.rsiLen, len(self.mainData)):
      moneyFlow[i] = self.mainData.Volume[i]*(self.mainData.High[i] + self.mainData.Low[i] + self.mainData.Close[i])/3
      sumGain = 0
      sumLoss = 0
      sumPosFlow = 0
      sumNegFlow = 0
      for j in range(0, self.rsiLen):
        diff = self.mainData.Close[i-j] - self.mainData.Open[i-j] 
        if diff > 0:
          sumGain = sumGain + diff 
          sumPosFlow = sumPosFlow + moneyFlow[i-j]
        else:
          sumLoss = sumLoss - diff
          sumNegFlow = sumNegFlow + moneyFlow[i-j]
      rs = sumGain/sumLoss
      mf = sumPosFlow/sumNegFlow
      self.rsi[i] = 100 - 100/(1+rs)    
      self.mfi[i] = 100 - 100/(1+mf)

    #Bollinger
    avg = pd.stats.moments.rolling_mean(self.mainData.Close, self.bollingerLength)
    std = pd.stats.moments.rolling_std(self.mainData.Close, self.bollingerLength)  
    self.bollingerHigh = avg + (std*self.bollingerSig)
    self.bollingerLow = avg - (std*self.bollingerSig)

  def plot(self):
    if len(self.mainData.index) is 0:
      return

    self.fig = plt.figure()

    if self.mktStrategy.label == 'No Strategy':
      trendSubplot = 211
      MACDSubplot = 413
      stochSubplot = 414
    else:
      trendSubplot = 211
      MACDSubplot = 614
      stochSubplot = 615
      plt.subplot(616)
      plt.title('Strategy: ' + self.mktStrategy.label)
      plt.ylabel('Value ($)')
      plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1],
               self.mktStrategy.cash[self.startIdx:self.endIdx+1], 
               'b', label='Cash', hold=True)
      plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1],
               self.mktStrategy.assets[self.startIdx:self.endIdx+1], 
               'k', label='Securities', hold=True)
      plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1],
               self.mktStrategy.equity[self.startIdx:self.endIdx+1], 
               'g', label='Total Equity', hold=True)
      plt.grid()
      plt.legend(loc='best') 
    
      print('========================================================================')
      print('Strategy stats:')
      print('Total Appreciation: ' + str(self.mktStrategy.totalAppreciation) + ' percent.')
      print('Cash invested: ' + str(self.mktStrategy.cashBaseline))
      print('End Equity: ' + str(self.mktStrategy.totalEquity))
      print('Commissions: ' + str(self.mktStrategy.commissionOverhead))
      print('========================================================================')


    ax = self.fig.add_subplot(trendSubplot)

    #If we're plotting less than 360 days, plot original as a candle chart
    if self.endIdx-self.startIdx < 360:
      quotes = []
      for i in range(self.startIdx,self.endIdx+1):
        theDate = date2num(self.mainData.Date[i])
        quotes.append( (theDate, 
                        self.mainData.Open[i],
                        self.mainData.Close[i],
                        self.mainData.High[i],
                        self.mainData.Low[i]) ) 

      matplotlib.finance.candlestick_ochl(ax, quotes, width=0.5, colorup='g', colordown='r') 
      ax.xaxis.set_major_formatter(matplotlib.dates.AutoDateFormatter(matplotlib.dates.DayLocator())) 

    #Plot the price
    plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1], 
             self.mainData.Close[self.startIdx:self.endIdx+1], 
             label=(self.mainDataSymbol + ' Close'), color='k', hold=True)

    #Plot bollinger bands if applicable
    if self.enableBollinger is True:

      plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1], 
               self.bollingerHigh[self.startIdx:self.endIdx+1], 
               linestyle='--', 
               color='c', 
               label='Bollinger', 
               hold=True)
      plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1],
               self.bollingerLow[self.startIdx:self.endIdx+1], 
               linestyle='--', 
               color='c', 
               label='Bollinger', 
               hold=True) 

    for i in range(0,len(self.overlayList)):
      begin = self.getStartDateIdx(self.overlayList[i].dates)
      end = self.getEndDateIdx(self.overlayList[i].dates)
      plt.plot(self.overlayList[i].dates[begin:end+1], 
               self.overlayList[i].prices[begin:end+1], 
               label=self.overlayList[i].label, hold=True)

    #If using a strategy, plot the buy and sell commands
    if self.mktStrategy.label != 'No Strategy':
      buyDates = []
      buyPrices = []
      sellDates = []
      sellPrices = []
      for i in range(0, len(self.mktStrategy.buyCmds)):
        if (self.mktStrategy.buyCmds[i] != 0):
          buyDates.append(self.mainData.Date[i])
          buyPrices.append( self.mainData.Low[i] + (self.mainData.High[i]-self.mainData.Low[i])/2 )
        elif (self.mktStrategy.sellCmds[i] != 0):
          sellDates.append(self.mainData.Date[i])
          sellPrices.append( self.mainData.Low[i] + (self.mainData.High[i]-self.mainData.Low[i])/2 )    
      plt.plot(buyDates, buyPrices, "^", color='c', label='Buy Cmd')
      plt.plot(sellDates, sellPrices, "v", color='m', label='Sell Cmd')
    plt.grid()
    plt.legend(loc='best')

    ax2 = ax.twinx() 
    volMax = np.amax(self.mainData.Volume[self.startIdx:self.endIdx+1])
    plt.bar(self.mainData.Date[self.startIdx:self.endIdx+1],
            self.mainData.Volume[self.startIdx:self.endIdx+1],
            color='k', alpha=0.3, hold=True, width=0.5)
    ax2.set_ylim([0,volMax*4])

    if self.mainDataSymbol == 'NONE':
      plt.title('Market Price')
    else:
      plt.title('Market Price: ' + self.mainDataSymbol)
    plt.ylabel('Price ($)')



    plt.subplot(MACDSubplot)
    plt.ylabel('MACD')
    startIdx = self.getStartDateIdx(self.mainData.Date)
    endIdx = self.getEndDateIdx(self.mainData.Date)
    plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1], self.MACD[self.startIdx:self.endIdx+1], color='k', hold=True)
    plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1], self.MACDsignal[self.startIdx:self.endIdx+1], color='r', hold=True)
    plt.bar(self.mainData.Date[self.startIdx:self.endIdx+1], self.MACDindicator[self.startIdx:self.endIdx+1], color='b', hold=True)
    plt.grid()   

    line66 = [66]*len(self.mainData.Date)
    line50 = [50]*len(self.mainData.Date)
    line33 = [33]*len(self.mainData.Date)

    ax = plt.subplot(stochSubplot)
    plt.ylabel('Stochastics')
    plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1], self.rsi[self.startIdx:self.endIdx+1], color='r', label='RSI', hold=True)
    plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1], self.mfi[self.startIdx:self.endIdx+1], color='g', label='MFI', hold=True)
    plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1], line66[self.startIdx:self.endIdx+1], color='k', alpha=0.4, hold=True)
    plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1], line50[self.startIdx:self.endIdx+1], color='k', alpha=0.4, hold=True)
    plt.plot(self.mainData.Date[self.startIdx:self.endIdx+1], line33[self.startIdx:self.endIdx+1], color='k', alpha=0.4, hold=True)
    #plt.fill_between(self.mainData.Date[self.startIdx:self.endIdx+1], 
    #                 self.rsi[self.startIdx:self.endIdx+1], 
    #                 line66[self.startIdx:self.endIdx+1], 
    #                 where=np.array(self.rsi[self.startIdx:self.endIdx+1])>=np.array(line66[self.startIdx:self.endIdx+1]), 
    #                 color='r', alpha=0.5)
    #plt.fill_between(self.mainData.Date[self.startIdx:self.endIdx+1], 
    #                 self.rsi[self.startIdx:self.endIdx+1], 
    #                 line33[self.startIdx:self.endIdx+1], 
    #                 where=np.array(self.rsi[self.startIdx:self.endIdx+1])<=np.array(line33[self.startIdx:self.endIdx+1]), 
    #                 color='g', alpha=0.5)
    plt.legend(loc='best')
    ax.set_ylim([0,100])
    plt.grid()


    plt.show()

  def getStartDateIdx(self, dateArry):
    for i in range(0,len(dateArry)):
      if dateArry[i].year >= self.startYear:
        if dateArry[i].month >= self.startMonth:
          if dateArry[i].day >= self.startDay:
            return i
    return len(dateArry)-1

  def getEndDateIdx(self, dateArry):
    for i in range(0,len(dateArry)):
      if dateArry[i].year >= self.endYear:
        if dateArry[i].month >= self.endMonth:
          if dateArry[i].day >= self.endDay:
            return i
    return len(dateArry)-1

  def reDate(self, startDay, startMonth, startYear, endDay, endMonth, endYear):
    self.startDay = startDay
    self.startMonth = startMonth
    self.startYear = startYear
    self.endDay = endDay
    self.endMonth = endMonth
    self.endYear = endYear
    self.startIdx = self.getStartDateIdx(self.mainData.Date)
    self.endIdx = self.getEndDateIdx(self.mainData.Date)

  def toggleBollinger(self, length):
    self.bollingerLength = length
    if self.enableBollinger is True and self.bollingerLength == length:
      self.enableBollinger = False
      return False
    else:
      self.enableBollinger = True
      #Bollinger
      avg = pd.stats.moments.rolling_mean(self.mainData.Close, self.bollingerLength)
      std = pd.stats.moments.rolling_std(self.mainData.Close, self.bollingerLength)  
      self.bollingerHigh = avg + (std*self.bollingerSig)
      self.bollingerLow = avg - (std*self.bollingerSig)
      return True
      

  def addSimpMovingAvg(self, nDays):
    for i in range(0,len(self.overlayList)):
      if self.overlayList[i].label == (str(nDays) + '-day SMA'):
        olayCpy = self.overlayList
        self.overlayList = []
        for j in range(0,len(olayCpy)):
          if i is not j:
            self.overlayList.append(olayCpy[j])
        return False
        
    dataMA = np.convolve(self.mainData.Close.as_matrix(), np.ones((nDays,))/nDays, mode='valid')[(nDays-1):]
    xAxis = self.mainData.index[nDays-1:len(self.mainData.index)-nDays+1]
    avgdDates = self.mainData.Date[nDays-1:len(self.mainData.Date)-nDays+1]
    self.overlayList.append(po.PlotOverlay(dates=avgdDates, prices=dataMA, label='{d}-day SMA'.format(d=nDays)))
    return True

  def addExpMovingAvg(self, nDays):
    for i in range(0,len(self.overlayList)):
      if self.overlayList[i].label == (str(nDays) + '-day EMA'):
        olayCpy = self.overlayList
        self.overlayList = []
        for j in range(0,len(olayCpy)):
          if i is not j:
            self.overlayList.append(olayCpy[j])
        return False
        
    emaSpan = (nDays-1)/2
    ewma = pd.ewma(self.mainData.Close, span=emaSpan)
    self.overlayList.append(pl.PlotLine(dates=self.mainData.Date, prices=ewma, label='{d}-day EMA'.format(d=nDays)))
    return True

def fmt_vol(x,pos):
    if pos>3: return ''  # only label the first 3 ticks
    return '%dM' % int(x*1e-6)




