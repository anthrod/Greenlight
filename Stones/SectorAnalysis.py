#!/usr/bin/env python

import pandas
import numpy
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import datetime

dataDir = '/home/anthrod/Workspace/scratch/GreenLight/data'
dbName = '/snp500.h5'

dbPath = dataDir + dbName

def GetSectorNames():
  names = []
  names.append('industrials')
  names.append('energy')
  names.append('consumer_discretionary')
  names.append('utilities')
  names.append('telecommunications_services')
  names.append('materials')
  names.append('health_care')
  names.append('real_estate')
  names.append('consumer_staples')
  names.append('financials')
  names.append('information_technology')
  return names


def PlotSectorRaw(sectorName, startYear, endYear):
  data = pandas.read_hdf(dbPath, key=sectorName)
  plt.ion()
  plt.figure()
  startDay = datetime.datetime(day=1,month=1,year=startYear)
  endDay   = datetime.datetime(day=1,month=1,year=endYear)
  for i in range(0,len(data.minor_axis)):
    ticker = data.minor_axis[i]
    print('Parsing ' + ticker)
    df = data.minor_xs(ticker)
    df = df[df.index >= startDay]
    df = df[df.index <= endDay]
    plt.plot(df.index, df['close'])
  plt.title(sectorName)
  plt.grid()
  plt.show()

def Perturbations(sectorName, startYear, endYear, plot=False):
  data = pandas.read_hdf(dbPath, key=sectorName)
  if plot:
    plt.figure()
  startDay = datetime.datetime(day=1,month=1,year=startYear)
  endDay   = datetime.datetime(day=1,month=1,year=endYear)
 
  dates = data.major_axis[data.major_axis >= startDay]
  dates = dates[dates <= endDay]

  perturbations = []
  prevday = dates[0]

  #Iterate through all dates:
  for day in dates:
    gains = [0.0]   
    #Iterate through all tickers
    for j in range(0,len(data.minor_axis)):
      ticker = data.minor_xs(data.minor_axis[j])
      currClose = ticker.close[day]
      prevClose = ticker.close[prevday]
      if not numpy.isnan(currClose) and not numpy.isnan(prevClose):
        thisGain = (currClose-prevClose)/prevClose
        if not numpy.isnan(thisGain):
          gains.append(thisGain)
    perturbations.append(numpy.mean(gains))
    prevday = day

  if plot:
    plt.bar(dates, perturbations)
    plt.title('Perturbations: ' + sectorName)
    plt.grid()
    plt.show()
  return dates, perturbations

def Integral(data):
  integral = []
  integration = 0
  for pt in data:
    integration = integration + pt
    integral.append(integration)
  return integral
  

def CycleIntegration(sector, plot=False):
  startYear = 1986
  endYear   = 2017

  if plot:
    plt.figure()
    plt.subplot(2,1,1)

  integration = [0]*366 #range(1,365+1)

  years = range(startYear, endYear+1)
  sectors = GetSectorNames()
  colors = cm.rainbow(numpy.linspace(0, 1, len(years)))
  dateVec = []
  pertVec = []
  for year, color in zip(years, colors):
    dates, perts = Perturbations(sector, year, year+1)
    doys = []
    for i in range(0,len(dates)):
      doy = dates[i].timetuple().tm_yday
      #print(str(doy) + ' ' + str(i))
      doys.append(doy)
      integration[doy-1] = integration[doy-1] + perts[i]  
    plt.plot(doys, pandas.rolling_mean(numpy.array(perts),20), label=str(year), color=color, hold=True)
    print str(year)

  if plot:
    plt.legend(loc='best')
    plt.grid()
    plt.subplot(212)
    plt.plot(range(0,366), pandas.rolling_mean(numpy.array(integration),80))
    plt.grid()
    plt.show()  
  

def Run():
  startDay = 2016
  endDay = 2017
  sectors = GetSectorNames()
  plt.ion()

  plt.figure()
  colors = cm.rainbow(numpy.linspace(0, 1, len(sectors)))

  dateVec = []
  pertVec = []

  for sector, color in zip(sectors, colors):
    dates, perts = Perturbations(sector, startDay, endDay, plot=False)
    #perts = pandas.rolling_mean(numpy.array(perts), 20)
    plt.plot(dates, perts, label=sector, color=color, hold=True)
    dateVec.append(dates)
    pertVec.append(perts)
    print sector

  pertVec = numpy.array(pertVec)
  pertMean = pertVec.mean(axis=0)
  pertDiffs = pertVec

  plt.plot(dateVec[0], pertMean, label='Mean', color='k')

  plt.legend(loc='best')
  plt.grid()
  plt.show()


  plt.figure()
  colors = cm.rainbow(numpy.linspace(0, 1, len(sectors)))
  for i, color in zip(range(len(pertVec)), colors):
    pertDiffs[i] = pertVec[i] - pertMean[i]
    #diff = pandas.rolling_mean(pertDiffs[i], 20)
    plt.plot(dateVec[i], pertDiffs[i], label=sectors[i], color=color, hold=True)
  plt.legend(loc='best')
  plt.grid()
  plt.show()


  


if __name__ == '__main__':
    CycleIntegration('telecommunications_services', plot=True)
    input("Press [enter] to continue.")


