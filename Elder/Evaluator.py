import matplotlib.pyplot as plt
import numpy as np

class Evaluator(object):
  def __init__(self):
    self.buyHistory = []
    self.sellHistory = []
    self.cashHistory = []
    self.securityHistory = []
    self.commissionHistory = []
    self.incomeHistory = []
    self.totalPay = 0
    self.totalCommissions = 0

  def logBuy(self, security, amount, day):
    self.buyHistory.append( [day, security.name, amount] )
    self.totalCommissions = self.totalCommissions + security.commissionCost

  def logSell(self, security, amount, day):
    self.sellHistory.append( [day, security.name, amount] )
    self.totalCommissions = self.totalCommissions + security.commissionCost 
 
  def logCash(self, day, balance):
    self.cashHistory.append( [day, balance] )
  
  def logCommission(self, day, commissionAmt):
    self.commissionHistory = [day, commissionAmt]
  
  def logIncome(self, day, payAmt):
    self.incomeHistory.append( [day, payAmt] )
    self.totalPay = self.totalPay + payAmt

  def evaluate(self, cash, security, plots=False):
    totalAssets = cash.balance + security.investedAmount
    totalAppreciation = 100 * (totalAssets - self.totalPay) / self.totalPay

    print('============================================')
    print('Original capital: ' + str(self.totalPay))
    print('Amount in bank: ' + str(cash.balance))
    print('Amount invested: ' + str(security.investedAmount))
    print('Total gains: ' + str(totalAppreciation) + '%')
    print('Total commissions: ' + str(self.totalCommissions))

    buyDates = []
    buyPrices = []
    for i in range(0,len(self.buyHistory)):
      buyDates.append(self.buyHistory[i][0])
      buyPrices.append( security.dailyHistory['Adj Close'][self.buyHistory[i][0]] )

    sellDates = []
    sellPrices = []
    for i in range(0,len(self.sellHistory)):
      sellDates.append(self.sellHistory[i][0])
      sellPrices.append( security.dailyHistory['Adj Close'][self.sellHistory[i][0]] )

    if plots is True:
  
      fig = plt.figure()
      ax = fig.add_subplot(211)
      plt.xlim([security.dailyHistory.Date[0], security.dailyHistory.Date[len(security.dailyHistory.Date)-1]] )
      plt.plot(security.dailyHistory.Date, security.dailyHistory['Adj Close'], color='k', hold=True)
      bollinger = security.getIndicator( indicatorType = 'Bollinger' ) 
      bollingerHigh = bollinger.data['High']
      plt.plot(security.dailyHistory.Date, bollingerHigh, color='c', linestyle='--', hold=True)
      bollingerLow = bollinger.data['Low']
      plt.plot(security.dailyHistory.Date, bollingerLow, color='c', linestyle='--', hold=True)
      ema360 = security.getIndicator( indicatorType = 'EMA', movingAvgDays = 360 )
      ema180 = security.getIndicator( indicatorType = 'EMA', movingAvgDays = 180 )
      ema25 = security.getIndicator( indicatorType = 'EMA', movingAvgDays = 25 )
      plt.plot(security.dailyHistory.Date, ema360.data.Avg, color='r', linestyle='-', hold=True)
      plt.plot(security.dailyHistory.Date, ema180.data.Avg, color='g', linestyle='-', hold=True)
      plt.plot(security.dailyHistory.Date, ema25.data.Avg, color='m', linestyle='-', hold=True)

      plt.scatter(buyDates, buyPrices, color='g', hold=True)
      plt.scatter(sellDates, sellPrices, color='r', hold=True)

      ax2 = ax.twinx() 
      volMax = np.amax(security.dailyHistory.Volume)
      plt.bar(security.dailyHistory.Date,
              security.dailyHistory.Volume,
              color='k', alpha=0.3, hold=True, width=0.5)
      ax2.set_ylim([0,volMax*4])


      plt.grid()

      plt.subplot(413)
      plt.xlim([security.dailyHistory.Date[0], security.dailyHistory.Date[len(security.dailyHistory.Date)-1]] )
      macdData = security.getIndicator( indicatorType='MACD' )
      plt.plot(security.dailyHistory.Date, macdData.data.Black, color='k', hold=True)
      plt.plot(security.dailyHistory.Date, macdData.data.Red, color='r', hold=True)
      plt.bar(security.dailyHistory.Date, macdData.data.Hist, color='b', hold=True)
      plt.grid()

      plt.subplot(414)
      plt.xlim([security.dailyHistory.Date[0], security.dailyHistory.Date[len(security.dailyHistory.Date)-1]] )
      mfi = security.getIndicator( indicatorType='MFI' )
      rsi = security.getIndicator( indicatorType='RSI' )
      plt.plot(security.dailyHistory.Date, mfi.data.MFI, color='g')
      plt.plot(security.dailyHistory.Date, rsi.data.RSI, color='r')
      plt.grid()

      plt.show()










