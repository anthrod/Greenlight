from Elder.Evaluator import *

from datetime import *
import datetime

class Income(object):

  def __init__(self, 
               verbose = False,
               biweeklyIncome = 0, 
               appreciationPerYear = 0.0):
    self.verbose = verbose
    self.biweeklyIncome = biweeklyIncome 
    self.appreciationPerYear = appreciationPerYear
    self.lastRaise = 0
    self.lastPay = 0
    self.raiseHistory = []
    self.payIntegrate = 0

  def setStartDay(self, startDay):
    self.lastRaise = startDay
    self.lastPay = startDay - datetime.timedelta(days=14)
    self.raiseHistory.append( {startDay, self.biweeklyIncome} )

  def update(self, day, cashAccount, evaluator):
    if (day - self.lastRaise) >= datetime.timedelta(days=365):
      self.biweeklyIncome = self.biweeklyIncome*(1.0 + self.appreciationPerYear) 
      self.lastRaise = day
      self.raiseHistory.append( {day, self.biweeklyIncome} )
      if (self.verbose and self.appreciationPerYear is not 0.0): 
        print('Raise biweekly income to ' + str(self.biweeklyIncome) + ' on ' + str(day))
    if (day - self.lastPay) >= datetime.timedelta(days=14):
      cashAccount.deposit(self.biweeklyIncome)
      evaluator.logIncome(day=day, payAmt = self.biweeklyIncome)
      self.payIntegrate = self.payIntegrate + self.biweeklyIncome
      self.lastPay = day
      if (self.verbose): 
        print('Deposit ' + str(self.biweeklyIncome) + ' on ' + str(day))      
