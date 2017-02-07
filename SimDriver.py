

from Elder import Strategy
from Elder import Cash
from Elder import Income
from Elder import Security
from Elder import Evaluator
from Stones import Indicator

from pandas.io.data import DataReader
from datetime import datetime


class SimDriver(object):
  def __init__(self, verbose=False):
    self.verbose = verbose 
    #self.strategy = Strategy.CostAveragingStrategy()
    self.strategy = Strategy.SignalStrategy()
    self.bank     = Cash.Cash(verbose=False)
    self.income   = Income.Income(biweeklyIncome = 600, verbose=self.verbose) 
    self.eval     = Evaluator.Evaluator()
    self.securities = []
    
  def addSecurity(self, securityType, name, dailyHistoryDataFrame):
    self.securities.append( Security.Security(securityType, name, dailyHistoryDataFrame) )
    if (self.verbose):
      print('Added ' + str(securityType) + ' ' + str(name))

  def runSim(self):
    if len(self.securities) is 0:
      print('ERROR: No securities added to simulate against')
      return
    #Make sure all securities have same start/end day
    startDay = self.securities[0].startDate
    endDay = self.securities[0].endDate
    for currSec in self.securities:
      if currSec.startDate is not startDay or currSec.endDate is not endDay:
        print('ERROR start/end dates do not match')
    
    #initializations:
    self.income.setStartDay(startDay)

    prevDay = self.securities[0].dailyHistory.Date[0]


    for day in self.securities[0].dailyHistory.Date:
      self.income.update(day, self.bank, self.eval)
      self.bank.update(day, self.eval)
      self.securities[0].update(day, prevDay, self.eval)
      self.strategy.dailyUpdate(cash=self.bank, income=self.income, security=self.securities[0], day=day, evaluator=self.eval)
      prevDay = day


    self.eval.evaluate(cash=self.bank, security=self.securities[0], plots=True)


if __name__ == '__main__':
  driver = SimDriver(verbose=False)

  securityData = DataReader('^GSPC',
                            'yahoo', 
                            datetime(2007, 1, 1), 
                            datetime(2020, 1, 1))
  securityData.Date = securityData.index

  driver.addSecurity( 'Exchange Traded Fund', '^GSPC', securityData )
  driver.runSim()
  

