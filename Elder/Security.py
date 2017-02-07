from datetime import datetime
from datetime import timedelta

from Stones import Indicator

class Security(object):
  
  def __init__(self, securityType, name, dailyHistoryDataFrame):
    if (securityType!="Common Stock" and securityType!="Exchange Traded Fund"):
      print('ERROR: Unrecognized security type ' + securityType)
    self.name            = name
    self.securityType    = securityType
    self.dailyHistory    = dailyHistoryDataFrame
    self.startIdx        = 0
    self.endIdx          = len(dailyHistoryDataFrame)
    self.investedAmount  = 0
    self.startDate       = dailyHistoryDataFrame.Date[0]
    self.endDate         = dailyHistoryDataFrame.Date[len(dailyHistoryDataFrame.Date)-1]
    self.indicators      = []
    self.commissionCost  = 5.0
    self.investedAmount  = 0.0

  #returns pandas datetime-index dataframe depending on indicator type
  def getIndicator(self, 
                   indicatorType    = 'NA',
                   movingAvgDays    = 0,
                   bollingerSigma   = 1,
                   bollingerDays    = 45,
                   MACDlongLength   = 45, #26,
                   MACDshortLength  = 20, #12,
                   MACDsignalLength = 12,
                   rsiLength        = 45):

    indLabel = Indicator.GetLabel(indicatorType, movingAvgDays, bollingerSigma, bollingerDays, 
                                  MACDlongLength, MACDshortLength, MACDsignalLength, rsiLength)
    for ind in self.indicators:
      if ind.label==indLabel:
        return ind

    if (indicatorType is 'EMA'):
      indicator = Indicator.Indicator(indicatorType= 'EMA', movingAvgDays=movingAvgDays, data=self.dailyHistory)
      self.indicators.append( indicator )
      return indicator
    elif (indicatorType is 'SMA'):
      indicator = Indicator.Indicator(indicatorType= 'SMA', movingAvgDays=movingAvgDays, data=self.dailyHistory)
      self.indicators.append( indicator )
      return indicator
    elif (indicatorType is 'Bollinger'):
      indicator = Indicator.Indicator(indicatorType= 'Bollinger', bollingerSigma=bollingerSigma, bollingerDays=bollingerDays, data=self.dailyHistory)
      self.indicators.append( indicator )
      return indicator
    elif (indicatorType is 'MACD'):
      indicator = Indicator.Indicator(indicatorType = 'MACD', MACDlongLength=MACDlongLength, MACDshortLength=MACDshortLength, MACDsignalLength=MACDsignalLength, data=self.dailyHistory)
      self.indicators.append( indicator )
      return indicator
    elif (indicatorType is 'RSI'):
      indicator = Indicator.Indicator(indicatorType = 'RSI', movingAvgDays=movingAvgDays, data=self.dailyHistory)
      self.indicators.append( indicator )
      return indicator
    elif (indicatorType is 'MFI'):
      indicator = Indicator.Indicator(indicatorType = 'MFI', movingAvgDays=movingAvgDays, data=self.dailyHistory)
      self.indicators.append( indicator )
      return indicator
    else:
      print('WARNING: Not sure how to handle indicator ' + indicatorType)
      return []

  def getStartDateIdx(self):
    dateArry = dailyHistory.Date
    for i in range(0,len(dateArry)):
      if dateArry[i].year >= self.startDate.year:
        if dateArry[i].month >= self.startDate.month:
          if dateArry[i].day >= self.startDate.day:
            return i
    return len(dateArry)-1

  def getEndDateIdx(self):
    dateArry = dailyHistory.Date
    for i in range(0,len(dateArry)):
      if dateArry[i].year >= self.startDate.year:
        if dateArry[i].month >= self.startDate.month:
          if dateArry[i].day >= self.startDate.day:
            return i
    return len(dateArry)-1

  def reDate(self, startDay, startMonth, startYear, endDay, endMonth, endYear):
    self.startDay = datetime.datetime(year=startYear, month=startMonth, day=startDay)
    self.endDay   = datetime.datetime(year=endYear, month=endMonth, day=endDay)
    self.startIdx = self.getStartDateIdx()
    self.endIdx   = self.getEndDateIdx()
    self.startDay = dailyHistory.Date[startIdx]
    self.endDay   = dailyHistory.Date[endIdx]

  def update(self, day, prevDay, evaluator): 
    pctChange = self.dailyHistory['Adj Close'][day] - self.dailyHistory['Adj Close'][prevDay]
    pctChange = pctChange / self.dailyHistory['Adj Close'][prevDay]
    self.investedAmount = self.investedAmount*(1.0+pctChange)
    













