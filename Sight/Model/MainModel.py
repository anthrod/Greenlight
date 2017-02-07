########################################################################################################
#
#  MainModel: Underlying GreenLight functionality
#
#  Author: Anthony Rodriguez
#  Date: December 2016
#
########################################################################################################

from Sight.Model import Strategies
from Sight.View import MainView as mv
from pandas.io.data import DataReader
from datetime import datetime
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

class MainModel:
  def __init__(self):
    self.view = mv.MainView()
    self.symbolToDownload = 'NA'
    self.mktStrategy = Strategies.NoStrategy()
    

  def downloadSymbol(self, symbol):
    self.symbolToDownload = symbol
    self.downloadSymbolYahoo()

  def downloadSymbolYahoo(self):
    dataFrame = DataReader(self.symbolToDownload,
                           'yahoo', 
                           datetime(1950, 1, 1), 
                           datetime(2018, 1, 1))
    dataFrame.Date = dataFrame.index

    self.view.setMainData(dataFrame, self.symbolToDownload)

  def reDate(self, startDay, startMonth, startYear, endDay, endMonth, endYear):
    self.view.reDate(startDay, startMonth, startYear, endDay, endMonth, endYear)
  
  def plot(self):
    if not self.mktStrategy.label=='No Strategy':
      self.mktStrategy.setData(bollingerLow = self.view.bollingerLow,
                               bollingerHigh = self.view.bollingerHigh,
                               macdRed = self.view.MACDsignal,
                               macdBlack = self.view.MACD,
                               macdHist = self.view.MACDindicator)                             
      self.mktStrategy.RunStrat(self.view.mainData, self.view.startIdx, self.view.endIdx)
      Strategies.EvaluateStrat(mktData = self.view.mainData,
                               strat = self.mktStrategy, 
                               start = self.view.startIdx,
                               end   = self.view.endIdx)
      self.view.mktStrategy = self.mktStrategy
    self.view.plot()

  def toggleBollinger(self, length):
    return self.view.toggleBollinger(length)
 
  def addSimpMovingAvg(self, length):
    return self.view.addSimpMovingAvg(length)

  def addExpMovingAvg(self, length):
    return self.view.addExpMovingAvg(length)
