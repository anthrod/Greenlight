########################################################################################################
#
#  SigProc: Market Signal Processing
#
#  Author: Anthony Rodriguez
#  Date: December 2016
#
########################################################################################################

from Model import Strategies

class StratModel:
  def __init__(self):
    self.strategies = []
    self.stratLabels = []    

    self.strategies.append(Strategies.PriceAveraging())
    self.strategies.append(Strategies.BollingerLow())
    
    for strat in self.strategies:
      self.stratLabels.append(strat.label)

  def GetStrategyNames(self):
    return self.stratLabels
