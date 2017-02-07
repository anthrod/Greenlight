########################################################################################################
#
#  MainView: Main Window for GreenLight
#
#  Author: Anthony Rodriguez
#  Date: December 2016
#
########################################################################################################
import os
import time
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.finance
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from Control import plotlines as pl
from datetime import datetime as dt
from matplotlib.dates import num2date
from matplotlib.dates import date2num
from pandas.io.data import DataReader
from datetime import datetime
from View import PlotOverlay as po

class MainView(object):
  def __init__(self):   
    self.mainData = []
    self.mainDataSymbol = 'NONE'
    self.overlayList = []
    self.enableBollinger = False
    self.bollingerLength = 30
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

  def setMainData(self, dataFrame, symbol):
    self.mainData = dataFrame
    self.mainDataSymbol = symbol
    self.overlayList = []
    emaSpan = (self.MACDshort-1)/2
    emaShort = pd.ewma(self.mainData.Close, span=emaSpan)
    emaSpan = (self.MACDlong-1)/2
    emaLong = pd.ewma(self.mainData.Close, span=emaSpan)
    self.MACD = emaShort-emaLong
    emaSpan = (self.MACDsigLen-1)/2
    self.MACDsignal = pd.ewma(self.MACD, span=emaSpan)
    self.MACDindicator = self.MACD-self.MACDsignal

  def replot(self):
    if len(self.mainData.index) is 0:
      return

    self.fig = plt.figure()

    trendSubplot = 211
    MACDSubplot = 212

    startIdx = self.getStartDateIdx(self.mainData.Date)
    endIdx = self.getEndDateIdx(self.mainData.Date)

    #If we're plotting less than 360 days, plot original as a candle chart
    if endIdx-startIdx < 360:
      quotes = []
      ax = self.fig.add_subplot(211)
      for i in range(startIdx,endIdx+1):
        theDate = date2num(self.mainData.Date[i])
        quotes.append( (theDate, 
                        self.mainData.Open[i],
                        self.mainData.Close[i],
                        self.mainData.High[i],
                        self.mainData.Low[i]) ) 

      matplotlib.finance.candlestick_ochl(ax, quotes, width=0.6, colorup='g', colordown='r') 
      ax.xaxis.set_major_formatter(matplotlib.dates.AutoDateFormatter(matplotlib.dates.DayLocator()))

    #Plot the price
    plt.subplot(trendSubplot)
    plt.plot(self.mainData.Date[startIdx:endIdx], 
             self.mainData.Close[startIdx:endIdx], 
             label=(self.mainDataSymbol + ' Close'), color='k', hold=True)

    #Plot bollinger bands if applicable
    if self.enableBollinger is True:
      avg = pd.stats.moments.rolling_mean(self.mainData.Close, self.bollingerLength)
      std = pd.stats.moments.rolling_std(self.mainData.Close, self.bollingerLength)  
      upband = avg + (std*2)
      dnband = avg - (std*2)
      plt.plot(self.mainData.Date[startIdx:endIdx], 
               upband[startIdx:endIdx], 
               linestyle='--', 
               color='c', 
               label='Bollinger', 
               hold=True)
      plt.plot(self.mainData.Date[startIdx:endIdx],
               dnband[startIdx:endIdx], 
               linestyle='--', 
               color='c', 
               label='Bollinger', 
               hold=True) 

    for i in range(0,len(self.overlayList)):
      startIdx = self.getStartDateIdx(self.overlayList[i].dates)
      endIdx = self.getEndDateIdx(self.overlayList[i].dates)
      plt.plot(self.overlayList[i].dates[startIdx:endIdx], 
               self.overlayList[i].prices[startIdx:endIdx], 
               label=self.overlayList[i].label, hold=True)
 
    plt.grid()
    plt.legend(loc='best')
    if self.mainDataSymbol == 'NONE':
      plt.title('Market Price')
    else:
      plt.title('Market Price: ' + self.mainDataSymbol)
    plt.ylabel('Price ($)')

    plt.subplot(MACDSubplot)
    plt.title('MACD')
    startIdx = self.getStartDateIdx(self.mainData.Date)
    endIdx = self.getEndDateIdx(self.mainData.Date)
    plt.plot(self.mainData.Date[startIdx:endIdx], self.MACD[startIdx:endIdx], color='k', hold=True)
    plt.plot(self.mainData.Date[startIdx:endIdx], self.MACDsignal[startIdx:endIdx], color='r', hold=True)
    plt.bar(self.mainData.Date[startIdx:endIdx], self.MACDindicator[startIdx:endIdx], color='b', hold=True)
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
    self.replot()

  def toggleBollinger(self, length):
    if self.enableBollinger is True and self.bollingerLength == length:
      self.enableBollinger = False
      return False
    else:
      self.bollingerLength = length
      self.enableBollinger = True
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





