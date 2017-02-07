
import numpy as np
import pandas as pd

from matplotlib import pyplot as plt

class Indicator(object):
  def __init__(self,
               data,
               indicatorType    = 'NA',
               movingAvgDays    = 0,
               bollingerSigma   = 1,
               bollingerDays    = 45,
               MACDlongLength   = 26,
               MACDshortLength  = 12,
               MACDsignalLength = 9,
               rsiLength        = 60):
    self.type = indicatorType
    self.label = GetLabel(indicatorType, movingAvgDays, bollingerSigma, bollingerDays, MACDlongLength, MACDshortLength, MACDsignalLength, rsiLength)
    
    if indicatorType=='SMA':
      self.data = SMA(data=data, length=movingAvgDays)
    elif indicatorType=='EMA':
      self.data = EMA(data=data, length=movingAvgDays)
    elif indicatorType=='Bollinger':
      self.data = Bollinger(data=data, sigma=bollingerSigma, length=bollingerDays)
    elif indicatorType=='MACD':
      self.data = MACD(data=data, longLen=MACDlongLength, shortLen=MACDshortLength, sigLen = MACDsignalLength)
    elif indicatorType=='RSI':
      self.data = RSI(data=data, length=rsiLength)
    elif indicatorType=='MFI':
      self.data = MFI(data=data, length=rsiLength)
    else:
      print('ERROR: Could not handle indicator request for ' + str(indicatorType))   
  
def SMA(data, length):
  convolution = np.convolve(data['Adj Close'].as_matrix(), np.ones((length,))/length, mode='valid')[(length-1):]
  indices = data.Date[length-1:len(data)-length+1]
  dat = {'Avg':convolution}
  return pd.DataFrame(data=dat, index=indices)

def EMA(data, length):
  emaSpan = (length-1)/2
  ewma = pd.ewma(data['Adj Close'], span=emaSpan)
  dat = {'Avg':ewma}
  indices = data.Date 
  return pd.DataFrame(data=dat, index=indices)

def Bollinger(data, sigma, length):
  avg = pd.stats.moments.rolling_mean(data['Adj Close'], length)
  std = pd.stats.moments.rolling_std(data['Adj Close'], length)  
  bollingerHigh = avg + (std*sigma)
  bollingerLow = avg - (std*sigma)  
  dat = {'High':bollingerHigh, 'Low':bollingerLow}
  indices = data.Date
  return pd.DataFrame(data=dat, index=indices)

def MACD(data, longLen, shortLen, sigLen):
  emaSpan = (shortLen-1)/2
  emaShort = pd.ewma(data['Adj Close'], span=emaSpan)
  emaSpan = (longLen-1)/2
  emaLong = pd.ewma(data['Adj Close'], span=emaSpan)
  black = emaShort-emaLong
  emaSpan = (sigLen-1)/2
  red = pd.ewma(black, span=emaSpan)
  indicator = black-red
  dat = {'Black':black, 'Red':red, 'Hist':indicator}
  indices = data.Date
  return pd.DataFrame(data=dat, index=indices)

def RSI(data, length):
  rsi = [50]*len(data)
  avgGain = [0]*len(data)
  avgLoss = [0]*len(data)
  rs = 0  
  for i in range(length, len(data)):
    sumGain = 0
    sumLoss = 0
    for j in range(0, length):
      diff = data.Close[i-j] - data.Open[i-j] 
      if diff > 0:
        sumGain = sumGain + diff 
      else:
        sumLoss = sumLoss - diff  
    rs = sumGain/sumLoss
    rsi[i] = 100 - 100/(1+rs)    
  dat = {'RSI':rsi}
  indices = data.Date
  return pd.DataFrame(data=dat, index=indices)

def MFI(data, length):
  mfi = [50]*len(data)
  moneyFlow = [0]*len(data)
  for i in range(1,length):
    moneyFlow[i] = data.Volume[i]*(data.High[i] + data.Low[i] + data.Close[i])/3    
  for i in range(length, len(data)):
    moneyFlow[i] = data.Volume[i]*(data.High[i] + data.Low[i] + data.Close[i])/3
    sumPosFlow = 0
    sumNegFlow = 0
    for j in range(0, length):
      diff = data.Close[i-j] - data.Open[i-j] 
      if diff > 0:
        sumPosFlow = sumPosFlow + moneyFlow[i-j]
      else:
        sumNegFlow = sumNegFlow + moneyFlow[i-j]
    mf = sumPosFlow/sumNegFlow
    mfi[i] = 100 - 100/(1+mf)
  dat = {'MFI':mfi}
  indices = data.Date
  return pd.DataFrame(data=dat, index=indices)



def GetLabel( indicatorType    = 'NA',
              movingAvgDays    = 0,
              bollingerSigma   = 1,
              bollingerDays    = 45,
              MACDlongLength   = 26,
              MACDshortLength  = 12,
              MACDsignalLength = 9,
              rsiLength        = 11):
  if indicatorType=='NA':
    return 'NA'
  elif indicatorType=='SMA':
    return (str(movingAvgDays) + '-day SMA')
  elif indicatorType=='EMA':
    return (str(movingAvgDays) + '-day EMA')
  elif indicatorType=='Bollinger':
    return (str(bollingerDays) + '-day ' + str(bollingerSigma) + '-sigma' + ' bollinger')
  elif indicatorType=='MACD':
    return (str(MACDshortLength) + ' over ' + str(MACDlongLength) + ' MACD ' + str(MACDsignalLength))
  elif indicatorType=='RSI':
    return (str(rsiLength) + '-day RSI')
  elif indicatorType=='MFI':
    return (str(rsiLength) + '-day MFI')
  else:
    return 'NA'
