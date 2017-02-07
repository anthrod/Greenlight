#!/usr/bin/env python

import pandas
import numpy
from yahoo_finance import Share
import SectorAnalysis
from StockData import *
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import scipy
import scipy.stats
import urllib
import os
import MahonyScraper
import datetime
from bs4 import BeautifulSoup as bs
import urlparse
from urllib2 import urlopen
from urllib import urlretrieve
import os
import sys



dataDir   = '/home/anthrod/Workspace/scratch/GreenLight/data'
dbName    = '/snp500.h5'
fFileName = '/snpFins.csv' 
dbPath    = dataDir + dbName
ratiosDir = dataDir + '/Ratios'
finDir    = dataDir + '/Financials' 
fPath     = dataDir + fFileName
fProcPath = finDir + '/processed'
msKRstub  = 'http://financials.morningstar.com/ajax/exportKR2CSV.html?t='
msFinSeg1 = 'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t='
msFinSeg2 = '&reportType='
msFinSeg3 = '&period=12&dataType=A&order=asc&columnYear=5&number=3'

monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def GetSnpTickers():
  secNames = SectorAnalysis.GetSectorNames()
  snpTickers = []
  for sector in secNames:
    data = pandas.read_hdf(dbPath, key=sector)
    for ticker in data.minor_axis:
      snpTickers.append(ticker)
      print ticker 
  return snpTickers

def PullMorningstar():
  snpTickers = GetSnpTickers()
  puller     = urllib.URLopener()
  for ticker in snpTickers:
    print('Pulling data for ' + ticker)
    #Key Ratios:
    msURL = msKRstub + ticker
    try:
      puller.retrieve(msURL, ratiosDir + '/' + ticker + '.csv')
      #Income Statement
      msURL = msFinSeg1 + ticker + msFinSeg2 + 'is' + msFinSeg3
      puller.retrieve(msURL, finDir + '/IS_' + ticker + '.csv')
      #Cash Flow
      msURL = msFinSeg1 + ticker + msFinSeg2 + 'cf' + msFinSeg3
      puller.retrieve(msURL, finDir + '/CF_' + ticker + '.csv')    
      #Balance Sheet
      msURL = msFinSeg1 + ticker + msFinSeg2 + 'bs' + msFinSeg3
      puller.retrieve(msURL, finDir + '/BS_' + ticker + '.csv')    
    except IOError:
         print("ERROR: " + ticker)


def CreateYahooFile():
  snpTickers = GetSnpTickers()

  symbol = []
  cap = []
  book = []
  ebitda = []
  divShare = []
  divYield = []
  earnPerShare = []
  pe = []
  peg = []
  priceSales = []
  priceBook = []

  for ticker in snpTickers:
    tkr = Share(ticker)
    symbol.append(ticker)

    if tkr.get_market_cap():
      cap.append(tkr.get_market_cap())
    else:
      cap.append(0.0)

    if (tkr.get_book_value()):
      book.append(tkr.get_book_value())
    else:
      book.append(0.0)

    if (tkr.get_ebitda()):
      ebitda.append(tkr.get_ebitda())
    else:
      ebitda.append(0.0)

    if tkr.get_dividend_share():
      divShare.append(tkr.get_dividend_share())
    else:
      divShare.append(0.0)

    if tkr.get_dividend_yield():
      divYield.append(tkr.get_dividend_yield())
    else:
      divYield.append(0.0) 

    if tkr.get_earnings_share():
      earnPerShare.append(tkr.get_earnings_share())
    else:
      earnPerShare.append(0.0)

    if tkr.get_price_earnings_ratio():
      pe.append(tkr.get_price_earnings_ratio())
    else:
      pe.append(0.0)

    if tkr.get_price_earnings_growth_ratio():
      peg.append(tkr.get_price_earnings_growth_ratio())
    else:
      peg.append(0.0)

    if tkr.get_price_sales():
      priceSales.append(tkr.get_price_sales())
    else:
      priceSales.append(0.0)

    if tkr.get_price_book():
      priceBook.append(tkr.get_price_book())
    else:
      priceBook.append(0.0)

    print ('Cached ' + ticker)

  tickerDict =        {  'symbol':     symbol,
                         'cap':        cap,
                         'book':       book,
                         'ebitda':     ebitda,
                         'divShare':   divShare,
                         'divYield':   divYield,
                         'eps':        earnPerShare,
                         'pe':         pe,
                         'peg':        peg,
                         'priceSales': priceSales,
                         'priceBook':  priceBook }

  df = pandas.DataFrame(data=tickerDict)
  df.to_csv(path_or_buf=fPath, index=False)

def PlotRatios():
  df = pandas.read_csv(fPath)  
  plt.subplot(221)
  plt.title('P/E')
  cutoff = 60
  pe = df.pe[(df.pe < cutoff) & (df.pe>0.0)]
  plt.hist(pe, 75, normed=1, facecolor='cyan', alpha=0.75)
  dist = getattr(scipy.stats, 'lognorm')
  param = dist.fit(pe)
  fitPdf = dist.pdf(range(0,cutoff), *param[:-2], loc=param[-2], scale=param[-1])
  plt.plot(range(0,cutoff),fitPdf, color='black')
  plt.subplot(222)
  plt.title('P/B')
  cutoff = 10
  pb = df.priceBook[(df.priceBook < cutoff) & (df.priceBook>0.0)]
  plt.hist(pb, 75, normed=1, facecolor='magenta', alpha=0.75) 
  dist = getattr(scipy.stats, 'lognorm')
  param = dist.fit(pb)
  fitPdf = dist.pdf(range(0,cutoff), *param[:-2], loc=param[-2], scale=param[-1])
  plt.plot(range(0,cutoff),fitPdf, color='black')
  plt.subplot(223)
  plt.title('EPS')
  cutoff = 50
  eps = df.eps[(df.eps < cutoff) & (df.eps>0.0)]
  plt.hist(eps, 75, normed=1, facecolor='green', alpha=0.75)  
  dist = getattr(scipy.stats, 'lognorm')
  param = dist.fit(eps)
  fitPdf = dist.pdf(range(0,cutoff), *param[:-2], loc=param[-2], scale=param[-1])
  plt.plot(fitPdf, color='black')
  plt.subplot(224)
  plt.title('P/S')
  cutoff = 10
  ps = df.priceSales[df.priceSales<cutoff]
  plt.hist(ps, 75, normed=1, facecolor='orange', alpha=0.75)  
  dist = getattr(scipy.stats, 'lognorm')
  param = dist.fit(ps)
  fitPdf = dist.pdf(range(0,cutoff), *param[:-2], loc=param[-2], scale=param[-1])
  plt.plot(fitPdf, color='black')
  plt.grid()
  plt.show()

def AggregateFiles():
  #Get a list of unique tickers:
  tickers = []
  for filename in os.listdir(finDir):
    tickers.append(filename.split("_")[1].split(".")[0])
  tickers = set(tickers)
   
  if not os.path.exists(fProcPath):
    os.makedirs(fProcPath)

  for ticker in tickers:
    incomeStatement = open(finDir + '/IS_' + ticker + '.csv', 'r')
    cashFlow        = open(finDir + '/CF_' + ticker + '.csv', 'r')
    balanceSheet    = open(finDir + '/BS_' + ticker + '.csv', 'r')
    aggFile         = (fProcPath + '/' + ticker + '.csv')
    IStext = incomeStatement.read()
    CFtext = cashFlow.read()
    BStext = balanceSheet.read()
    aggText = IStext + CFtext + BStext
    aggFile = open(aggFile, "w")
    aggFile.write(aggText)
    aggFile.close()
    incomeStatement.close()
    cashFlow.close()
    balanceSheet.close()
    

def FetchAllData():
  MahonyScraper.get_snp500()
  PullMorningStar()
  AggregateFiles()


def GetDatum(dataStr, keyTerm, nArgs):
  for line in dataStr:
    if keyTerm in line:
      args = line.split(',')
      totalArgs = len(args)
      theStrings = args[totalArgs-nArgs:totalArgs+1]
      theNums = []
      for theStr in theStrings:
        if theStr=='':
          theNums.append(numpy.NaN)
        else:
          theNums.append(float(theStr))
      return theNums
  return [numpy.NaN] * 6

#Attempt to get gross profit from 
def GrossProfitFromGuruFocus(ticker):
  print 'Attempting to retrieve Gross Profit from GuruFocus'
  url = 'http://www.gurufocus.com/term/Gross+Profit/' + ticker + '/Gross-Profit/'
  soup = bs(urlopen(url), 'lxml')
  strongs = soup.find_all('strong')

  for i in range(0,len(strongs)):
    #print strongs[i].string
    dateVec = []
    numVec = []
    if 'Annual Data' in str(strongs[i]):
      #Build a vector of dates
      for j in range(i+1, len(strongs)):
        isDateEntry = False
        #Iterate across month names and see if the current arg is a date:
        for monthName in monthNames:
          if monthName in str(strongs[j]):
            yr = int(str(strongs[j])[11:13])+2000
            dateVec.append(datetime.datetime(year=yr, month=1, day=1))
            isDateEntry = True
        if 'Quarterly Data' in str(strongs[j]):
          return dateVec, numVec
        if not isDateEntry:
          theNum = str(strongs[j].string)
          if ',' in theNum:
            theNum = theNum.split(',')[0] + theNum.split(',')[1]
          elif theNum=='' or theNum=='None':
            theNum = numpy.NaN
          numVec.append(float(theNum))
  return [], []

      
  '''
  print soup.get_text()
  for n in range(0,len(lines)):
    if 'Annual Data' in lines[n]:
      dateStr = ''
      gpStr = ''
      for m in range(n,len(lines)):
        if 'Jan' in lines[m] or 'Feb' in lines[m] or 'Mar' in lines[m] or 'Apr' in lines[m] or 'May' in lines[m] \
          or 'Jun' in lines[m] or 'Jul' in lines[m] or 'Aug' in lines[m] or 'Sep' in lines[m] or 'Oct' in lines[m] \
          or 'Nov' in lines[m] or 'Dec' in lines[m]:
            dateStr = lines[m]
        if 'Gross_Profit' in lines[m]:
          gpStr = lines[m+1]
          break
      if dateStr=='' or gpStr=='':
        print 'Failed'
        return [], []
      else:
        mon = dateStr[0:3]
        dates = dateStr.split(mon)[1:len(dateStr.split(mon))]
        gps = gpStr.split(',') 
        outDates = []
        for date in dates:
          outDates.append(datetime.datetime(day=1,month=1,year=int(date)+2000))
        outGPs = []
        for gp in gps:
          outGPs.append(float(gp))
        return outDates, outGPs
  '''
        


#Quantitative Value metrics
def GetMetricsFrames(plot=False):
  tickers = []
  #Read all aggregated file names to get tickers:
  for filename in os.listdir(fProcPath):
    tickers.append(filename.split(".")[0])
  tickers = set(tickers)

  stocks = []

  nSuccess = 0

  #Iterate through the csv files
  for ticker in tickers:
    valid = True
    inFile = open(fProcPath + '/' + ticker + '.csv', 'r')
    tkTxt  = inFile.read()
    tkTxt = tkTxt.split('\n')

    #Get dates for data
    dates = []
    for line in tkTxt:
      if 'Fiscal year ends in' in line:
        args = line.split(',')
        dates = args[1:6]
        for i in range(0,len(dates)):
          dates[i] = datetime.datetime(year=int(dates[i].split('-')[0]), month=12, day=1)
        #Append 1 more year (the 'TTM' term)
        dates.append(datetime.datetime(year=dates[4].year+1, month=12, day=1))
    if dates==[]:
      print('No dates for ' + ticker)
      continue
    '''   
    #EBIT (if no EBIT (earnings come from interest), return NaN array)
    EBIT = GetDatum(tkTxt, 'Operating income', 6)    

    #Capital: fixed assets + current assets - current liabilities - cash
    #Total Enterprise value: cap + total debt - excess cash + preferred stock + minority interests
    fixedAssets = GetDatum(tkTxt, '\"Net property, plant and equipment\"', 5)
    fixedAssets.append(numpy.NaN)
    currentAssets = GetDatum(tkTxt, 'Total current assets', 5)
    currentAssets.append(numpy.NaN)
    currentLiabilities = GetDatum(tkTxt, 'Total current liabilities', 5)
    currentLiabilities.append(numpy.NaN)
    cash = GetDatum(tkTxt, 'Total cash', 5)
    cash.append(numpy.NaN)

    yahooTkr = Share(ticker)
    currCap = numpy.NaN
    if yahooTkr.get_market_cap():
      currCap = yahooTkr.get_market_cap()
      if 'B' in currCap:
        currCap = float(currCap.split('B')[0]) * 1000
      else:
        currCap = float(currCap) 
    else:
      print('WARNING could not get mkt cap for ' + tracker)
      currCap = numpy.NaN   

    stDebt     = GetDatum(tkTxt, 'Short-term debt', 5)
    ltDebt     = GetDatum(tkTxt, 'Long-term debt', 5)

    currPreferredStock = 0
    #if yahooTkr.get_dividend_yield() and yahooTkr.get_price():
    #  currPreferredStock = float(yahooTkr.get_dividend_yield()) / float(yahooTkr.get_price()) 
    #else:
    #  currPreferredStock = 0.0
    '''

    GPAsuccessful = True

    #Gross profit: First, pull from MorningStar
    grossProfit = GetDatum(tkTxt, 'Gross profit', 6)
    if numpy.isnan(grossProfit[4]):
      #If this fails, try to retrieve from GuruFocus
      print('Could not retrieve Morningstar Gross Profit for ' + ticker)
      theseDates, grossProfit = GrossProfitFromGuruFocus(ticker)
      if theseDates==[] or grossProfit==[]:
        print('Could not resolve Gross profit for ' + ticker)
        GPAsuccessful = False
      else:
        theseDates = theseDates[len(theseDates)-6:len(theseDates)]


    totalAssets = GetDatum(tkTxt, 'Total assets', 5)
    if numpy.isnan(totalAssets[4]):
      print('Could not retrieve Total Assets for ' + ticker)
      GPAsuccessful = False


    totalAssets.append(numpy.NaN)


    '''
    capital        = []
    workingCapital = []
    buffetROC      = []
    greenblattROC  = []
    excessCash     = []
    TEV            = []
    earningsYield  = []

    for i in range(0,6):
      if pandas.isnull(fixedAssets[i]) or pandas.isnull(currentAssets[i]) or pandas.isnull(currentLiabilities[i]) or pandas.isnull(cash[i]) \
         or pandas.isnull(stDebt[i]) or pandas.isnull(ltDebt[i]) \
         or pandas.isnull(EBIT[i]) or EBIT[i]=='' or fixedAssets[i]=='' or currentAssets[i]=='' or currentLiabilities[i]=='' or cash[i]=='' \
         or stDebt[i]=='' or ltDebt[i]=='':
        capital.append(numpy.NaN)
        buffetROC.append(numpy.NaN)
        workingCapital.append(numpy.NaN)
        greenblattROC.append(numpy.NaN)
        excessCash.append(numpy.NaN)
        TEV.append(numpy.NaN)
        earningsYield.append(numpy.NaN)
      else:
        capital.append((int(fixedAssets[i])+int(currentAssets[i])-int(currentLiabilities[i])-int(cash[i])))
        buffetROC.append(float(EBIT[i]) / float(capital[i]))
        workingCapital.append( int(fixedAssets[i])+int(currentAssets[i])-int(currentLiabilities[i]) )
        greenblattROC.append( float(EBIT[i]) / float(workingCapital[i]) )
        excessCash.append( float(cash[i]) + float(currentAssets[i]) - float(currentLiabilities[i]) )
        TEV.append( float(currCap) + float(stDebt[i]) + float(ltDebt[i]) - float(excessCash[i]) + float(currPreferredStock) )
        earningsYield.append( float(EBIT[i]) / float(TEV[i]) )
    '''

    GPA = []

    #Gross profit to total assets, book value to mkt cap
    for i in range(0,6):
      if not GPAsuccessful or totalAssets[i]==0.0 or pandas.isnull(grossProfit[i]) or pandas.isnull(totalAssets[i]) \
        or grossProfit[i]=='' or totalAssets[i]=='':
        GPA.append(numpy.NaN)
      else:
        GPA.append(float(grossProfit[i]) / float(totalAssets[i]))

    yahooTkr = Share(ticker)
    inv_PB = numpy.NaN
    if yahooTkr.get_price_book():
      inv_PB = 1.0 / float(yahooTkr.get_price_book())
    else:
      print('WARNING could not get price/book for ' + ticker)
      print('Trying to calculate it manually...')
      bookValue = GetDatum(tkTxt, 'Total stockholders\' equity', 5)
      if bookValue[4]=='' or numpy.isnan(bookValue[4]):
        print('Could not calculate book price for ' + ticker)
        GPAsuccessful = False
      else:
        price = yahooTkr.get_price()
        inv_PB = float(bookValue[4]) / float(price)  
 
    if numpy.isnan(GPA[4]):
      print('WARNING: Could not calculate GPA for ' + ticker)
      GPAsuccessful = False

    if GPAsuccessful is True:
      stocks.append(StockData(name=ticker, GPA=GPA, invPriceBook=inv_PB))
      print('Successfully processed ' + ticker)
      nSuccess = nSuccess+1

  print (str(nSuccess) + ' successful reads.')

  if plot is True: 
    plt.show()
  return stocks


def ValueHistograms(stocks):

  GPAs = []

  for stock in stocks:
    GPAs.append(stock.GPA[4])

  plt.hist(GPAs, 75, normed=1, facecolor='cyan', alpha=0.75)

  '''
  df = pandas.read_csv(fPath)  
  plt.subplot(221)
  plt.title('GPA')
  cutoff = 60
  pe = df.pe[(df.pe < cutoff) & (df.pe>0.0)]
  plt.hist(pe, 75, normed=1, facecolor='cyan', alpha=0.75)
  dist = getattr(scipy.stats, 'lognorm')
  param = dist.fit(pe)
  fitPdf = dist.pdf(range(0,cutoff), *param[:-2], loc=param[-2], scale=param[-1])
  plt.plot(range(0,cutoff),fitPdf, color='black')
  plt.subplot(222)
  plt.title('P/B')
  cutoff = 10
  pb = df.priceBook[(df.priceBook < cutoff) & (df.priceBook>0.0)]
  plt.hist(pb, 75, normed=1, facecolor='magenta', alpha=0.75) 
  dist = getattr(scipy.stats, 'lognorm')
  param = dist.fit(pb)
  fitPdf = dist.pdf(range(0,cutoff), *param[:-2], loc=param[-2], scale=param[-1])
  plt.plot(range(0,cutoff),fitPdf, color='black')
  plt.subplot(223)
  plt.title('EPS')
  cutoff = 50
  eps = df.eps[(df.eps < cutoff) & (df.eps>0.0)]
  plt.hist(eps, 75, normed=1, facecolor='green', alpha=0.75)  
  dist = getattr(scipy.stats, 'lognorm')
  param = dist.fit(eps)
  fitPdf = dist.pdf(range(0,cutoff), *param[:-2], loc=param[-2], scale=param[-1])
  plt.plot(fitPdf, color='black')
  plt.subplot(224)
  plt.title('P/S')
  cutoff = 10
  ps = df.priceSales[df.priceSales<cutoff]
  plt.hist(ps, 75, normed=1, facecolor='orange', alpha=0.75)  
  dist = getattr(scipy.stats, 'lognorm')
  param = dist.fit(ps)
  fitPdf = dist.pdf(range(0,cutoff), *param[:-2], loc=param[-2], scale=param[-1])
  plt.plot(fitPdf, color='black')
  '''
  plt.grid()
  plt.show()


if __name__ == '__main__':
  stocks = GetMetricsFrames(plot=True)
  ValueHistograms(stocks)






















