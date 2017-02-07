########################################################################################################
#
#  SecurityHistory: History and identifier data for a single security
#
#  Author: Anthony Rodriguez
#  Date: December 2016
#
########################################################################################################

import pandas

class PlotOverlay:
  def __init__(self, dates, prices, label):
    self.prices  = prices
    self.dates   = dates
    self.label   = str(label)
