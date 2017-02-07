import datetime

class Cash(object):
  def __init__(self,  
               verbose = False,
               initialBalance = 0, 
               interestRate = 0,
               compoundRateMonths = 12):

    self.verbose = verbose
    self.balance = initialBalance
    self.interestRate = interestRate
    self.compoundRateMonths = compoundRateMonths
    self.balanceHistoryDaily = []

  def deposit(self, amount):
    self.balance = self.balance + amount

  def buy(self, theSecurity, theAmount, evaluator, day):
    if self.balance < theAmount+theSecurity.commissionCost:
      raise ValueError('Not enough cash in account to buy')
    self.balance = self.balance - theAmount - theSecurity.commissionCost
    theSecurity.investedAmount = theSecurity.investedAmount + theAmount
    evaluator.logBuy(theSecurity, theAmount, day)
    if (self.verbose):
      print('Bought ' + str(theAmount) + ' of ' + theSecurity.name)
      print(str(self.balance) + ' cash, ' + str(theSecurity.investedAmount) + ' total invested.\n')

  def sell(self, theSecurity, theAmount, evaluator, day):
    if theSecurity.investedAmount < theAmount:
      raise ValueError('Not enough invested to sell')
    self.balance = self.balance + theAmount
    theSecurity.investedAmount = theSecurity.investedAmount - theAmount
    self.balance = self.balance - theSecurity.commissionCost
    evaluator.logSell(theSecurity, theAmount, day)
    if (self.verbose):
      print('Sold ' + str(theAmount) + ' of ' + theSecurity.name)
      print(str(self.balance) + ' cash, ' + str(theSecurity.investedAmount) + ' total invested.\n')


  def update(self, amount, evaluator):
    self.balanceHistoryDaily.append(self.balance)
