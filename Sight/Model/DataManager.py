########################################################################################################
#
#  DataLoader: Responsible for loading ticker data from various sources. Also used for caching  
#              all data sets at runtime.
#
#  Author: Anthony Rodriguez
#  Date: December 2016
#
########################################################################################################

import pandas as pd
from pandas.io.data import DataReader
from datetime import datetime
import SecurityHistory

class DataManager:
  def __init__(self):
    self.cachedData = []
    self.americanSymbolFile = 'NONE'
    self.busy = False

  def loadAmericanSymbolsFromFileYahoo(self, symFile):
    self.americanSymbolFile = symFile
    self.loadAmericanSymbolsYahoo()

  def loadAmericanSymbolsYahoo(self):
    self.busy = True
    lines = [line.rstrip('\n') for line in open(self.americanSymbolFile)]
    for symbol in lines:
      data = DataReader(symbol,  'yahoo', datetime(1950, 1, 1), datetime(2018, 1, 1))
      self.cachedData.append( SecurityHistory.SecurityHistory(symbol, data) )
    self.busy = False

  def setAmericanSymbolFile(self, fileName):
    self.americanSymbolFile = fileName
