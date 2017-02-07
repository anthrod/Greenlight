########################################################################################################
#
#  MainControl: Main Controller for GreenLight
#
#  Author: Anthony Rodriguez
#  Date: December 2016
#
########################################################################################################

from PyQt4.QtGui import *
from PyQt4 import QtCore
from Sight.Model import MainModel as mm
from Sight.Model import Strategies
from threading import Thread
from time import sleep
import sys

class MainControl(QWidget):

  def __init__(self, width=800, height=600):
  
    self.mainModel = mm.MainModel()

    QWidget.__init__(self)
    self.resize(width, height)
    self.grid = QGridLayout()
    self.setLayout(self.grid)
    self.setGeometry(width, height, width, height)
    self.setWindowTitle('Greenlight')

    row = 1

    ########################TEXT OUTPUT#########################

    self.statusTextField = QLineEdit(self)
    self.statusTextField.setReadOnly(True)
    self.statusTextField.setText('Step into the Greenlight...')
    self.grid.addWidget(self.statusTextField, row, 3, 1, 2)

    ####################LOAD SYMBOL FILE############################

    row=row+1
    self.loadSymFileText = '/home/anthrod/Workspace/scratch/GreenWick/data/Config/symbols.txt'
    self.symFileTextField = QLineEdit(self)
    self.symFileTextField.textChanged.connect(self.loadSymFileTextChanged)
    self.symFileTextField.setText(self.loadSymFileText)
    self.grid.addWidget(self.symFileTextField, row, 1, 1, 3)

    self.loadSymFileBtn = QPushButton('Load Symbol File', self)
    self.loadSymFileBtn.clicked.connect(self.loadSymFileBtnPressed)
    self.grid.addWidget(self.loadSymFileBtn, row, 4, 1, 1)

    self.cachedSymText = 'VOO'
    self.cachedSymTextField = QLineEdit(self)
    self.cachedSymTextField.textChanged.connect(self.cachedSymTextChanged)
    self.cachedSymTextField.setText(self.cachedSymText)
    self.grid.addWidget(self.cachedSymTextField, row, 5, 1, 1)

    self.loadCachedSymBtn = QPushButton('Load Cached Symbol', self)
    self.loadCachedSymBtn.clicked.connect(self.loadCachedBtnPressed)
    self.grid.addWidget(self.loadCachedSymBtn, row, 6, 1, 1)

    ####################LOAD FROM CSV############################

    row=row+1
    defaultLoadFile = '/home/anthrod/Workspace/scratch/GreenWick/data/GSPC/gspc-daily-nodivs-1960-2016.csv'
    self.loadFileTextField = QLineEdit(self)
    self.loadFileTextField.textChanged.connect(self.loadFileTextChanged)
    self.loadFileTextField.setText(defaultLoadFile)
    self.grid.addWidget(self.loadFileTextField, row, 1, 1, 3)

    self.loadFileBtn = QPushButton('Load CSV data', self)
    self.loadFileBtn.clicked.connect(self.loadFileBtnPressed)
    self.grid.addWidget(self.loadFileBtn, row, 4, 1, 1)

    ####################LOAD FROM TICKER########################   

    self.symbol = 'VOO'
    self.pullSymbolTextField = QLineEdit(self)
    self.pullSymbolTextField.textChanged.connect(self.pullSymbolTextChanged)
    self.pullSymbolTextField.setText(self.symbol)
    self.grid.addWidget(self.pullSymbolTextField, row, 5, 1, 1)

    self.pullSymbolBtn = QPushButton('Download Symbol Data', self)
    self.pullSymbolBtn.clicked.connect(self.pullSymbolBtnPressed)
    self.grid.addWidget(self.pullSymbolBtn, row, 6, 1, 1)

    ###############SIMPLE MOVING AVERAGE########################

    row=row+1
    self.smaNumDays = 10
    self.smaDaysField = QLineEdit(self)
    self.smaDaysField.textChanged.connect(self.smaTextChanged)
    self.smaDaysField.setText(str(self.smaNumDays))
    self.grid.addWidget(self.smaDaysField, row, 1, 1, 1)

    self.smaBtn = QPushButton('SMA', self)
    self.smaBtn.clicked.connect(self.smaBtnPressed)
    self.grid.addWidget(self.smaBtn, row, 2, 1, 1)

    #############EXPONENTIAL MOVING AVERAGE####################
 
    self.emaDaysField = QLineEdit(self)
    self.emaDaysField.textChanged.connect(self.emaTextChanged)
    self.emaDaysField.setText('12')
    self.grid.addWidget(self.emaDaysField, row, 3, 1, 1)
    self.emaNumDays = 12

    self.emaLineBtn = QPushButton('EMA', self)
    self.emaLineBtn.clicked.connect(self.emaLineBtnPressed)
    self.grid.addWidget(self.emaLineBtn, row, 4, 1, 1)

    ##################BOLLINGER BANDS##########################
 
    self.bollingerLength = 45    
    self.bollingerField = QLineEdit(self)
    self.bollingerField.textChanged.connect(self.bollingerChanged)
    self.bollingerField.setText(str(self.bollingerLength))
    self.grid.addWidget(self.bollingerField, row, 5, 1, 1)
    #self.controller.setBollingerLength(self.bollingerLength)

    self.bollingerBtn = QPushButton('Bollinger Bands', self)
    self.bollingerBtn.clicked.connect(self.bollingerBtnPressed)
    self.grid.addWidget(self.bollingerBtn, row, 6, 1, 1)

    ########################START DATE##########################

    row=row+1
    self.startYearField = QLineEdit(self)
    self.startYearField.textChanged.connect(self.startYearChanged)
    self.startYearField.setText('1700')
    self.grid.addWidget(self.startYearField, row, 1, 1, 1)
    self.startYear = 0

    self.startMonthField = QLineEdit(self)
    self.startMonthField.textChanged.connect(self.startMonthChanged)
    self.startMonthField.setText('01')
    self.grid.addWidget(self.startMonthField, row, 2, 1, 1)
    self.startMonth = 0

    self.startDayField = QLineEdit(self)
    self.startDayField.textChanged.connect(self.startDayChanged)
    self.startDayField.setText('01')
    self.grid.addWidget(self.startDayField, row, 3, 1, 1)
    self.startDay = 0

    ##########################END DATE#############################

    #row=row+1
    self.endYearField = QLineEdit(self)
    self.endYearField.textChanged.connect(self.endYearChanged)
    self.endYearField.setText('3000')
    self.grid.addWidget(self.endYearField, row, 4, 1, 1)
    self.endYear = 3000

    self.endMonthField = QLineEdit(self)
    self.endMonthField.textChanged.connect(self.endMonthChanged)
    self.endMonthField.setText('12')
    self.grid.addWidget(self.endMonthField, row, 5, 1, 1)
    self.endMonth = 99

    self.endDayField = QLineEdit(self)
    self.endDayField.textChanged.connect(self.endDayChanged)
    self.endDayField.setText('30')
    self.grid.addWidget(self.endDayField, row, 6, 1, 1)
    self.endDay = 99

    ########################STRATEGIES############################

    row=row+1
    self.noStratBtn = QRadioButton('No Strategy')
    self.noStratBtn.setChecked(True)
    self.noStratBtn.toggled.connect(self.noStratBtnPressed)
    self.grid.addWidget(self.noStratBtn, row, 1, 1, 1)   

    self.priceAvgStratBtn = QRadioButton('Price Average')
    self.priceAvgStratBtn.setChecked(False)
    self.priceAvgStratBtn.toggled.connect(self.priceAvgStratBtnPressed)
    self.grid.addWidget(self.priceAvgStratBtn, row, 2, 1, 1)   

    self.signalStratBtn = QRadioButton('Signals')
    self.signalStratBtn.setChecked(False)
    self.signalStratBtn.toggled.connect(self.signalStratBtnPressed)
    self.grid.addWidget(self.signalStratBtn, row, 3, 1, 1)    

    ########################REFRESH PLOT############################

    row=row+1
    self.replotBtn = QPushButton('Refresh and Plot', self)
    self.replotBtn.clicked.connect(self.replotBtnPressed)
    self.grid.addWidget(self.replotBtn, row, 3, 1, 2)

    ####################SHOW###################################
  
    self.show()

  ######################GUI FUNCTIONS#########################

  def loadSymFileBtnPressed(self):
    #self.controller.loadFile(self.loadFileText)
    self.statusTextField.setText('Not implemented yet')

  def loadSymFileTextChanged(self, text):
    self.loadSymFileText = text

  def loadCachedBtnPressed(self):
    #self.controller.loadFile(self.loadFileText)
    self.statusTextField.setText('Not implemented yet.')

  def cachedSymTextChanged(self, text):
    self.cachedSymText = text

  def loadFileBtnPressed(self):
    #self.controller.loadFile(self.loadFileText)
    self.statusTextField.setText('Not implemented yet.')

  def loadFileTextChanged(self, text):
    self.loadFileText = text
    self.statusTextField.setText('Not implemented yet.')

  def pullSymbolTextChanged(self, text):
    self.symbolToPull = text

  def pullSymbolBtnPressed(self):
    self.statusTextField.setText('Pulling data for ' + self.symbolToPull + '...')
    self.mainModel.downloadSymbol( str(self.symbolToPull) )
    self.statusTextField.setText(self.symbolToPull + ' data loaded.')

  def smaBtnPressed(self):
    enabled = self.mainModel.addSimpMovingAvg(self.smaNumDays)
    if enabled is True:
      self.statusTextField.setText(str(self.smaNumDays) + '-day Simple Moving Average enabled')
    else:
      self.statusTextField.setText(str(self.smaNumDays) + '-day Simple Moving Average disabled')

  def smaTextChanged(self, text):
    self.smaNumDays = int(text)

  def emaTextChanged(self, text):
    self.emaNumDays = int(text)

  def emaLineBtnPressed(self):
    enabled = self.mainModel.addExpMovingAvg(self.emaNumDays)
    if enabled is True:
      self.statusTextField.setText(str(self.emaNumDays) + '-day Exponential Moving Average enabled')
    else:
      self.statusTextField.setText(str(self.emaNumDays) + '-day Exponential Moving Average disabled')

  def bollingerChanged(self, text):
    self.bollingerLength = int(text)

  def bollingerBtnPressed(self):
    enabled = self.mainModel.toggleBollinger(self.bollingerLength)
    if enabled==True:
      self.statusTextField.setText(str(self.bollingerLength) + '-day Bollinger Band enabled')
    else:
      self.statusTextField.setText(str(self.bollingerLength) + '-day Bollinger Band disabled')     

  def startYearChanged(self, text):
    self.startYear = int(text)

  def startMonthChanged(self, text):
    self.startMonth = int(text)

  def startDayChanged(self, text):
    self.startDay = int(text)

  def endYearChanged(self, text):
    self.endYear = int(text)

  def endMonthChanged(self, text):
    self.endMonth = int(text)

  def endDayChanged(self, text):
    self.endDay = int(text)

  def replotBtnPressed(self):
    self.statusTextField.setText('Greenlight GO!')
    self.mainModel.reDate(
                             startDay   = self.startDay,
                             startMonth = self.startMonth,
                             startYear  = self.startYear,
                             endDay     = self.endDay,
                             endMonth   = self.endMonth,
                             endYear    = self.endYear    )
    self.mainModel.plot()

  def resetAllStrats(self):
    self.noStratBtn.setChecked(False)
    self.priceAvgStratBtn.setChecked(False)
    self.signalStratBtn.setChecked(False)

  def noStratBtnPressed(self):
    if self.noStratBtn.isChecked()==True:
      self.resetAllStrats()
      self.noStratBtn.setChecked(True)
      self.mainModel.mktStrategy = Strategies.NoStrategy()

  def priceAvgStratBtnPressed(self):
    if self.priceAvgStratBtn.isChecked()==True:
      self.resetAllStrats()
      self.priceAvgStratBtn.setChecked(True)
      self.mainModel.mktStrategy = Strategies.PriceAveraging()

  def signalStratBtnPressed(self):
    if self.signalStratBtn.isChecked()==True:
      self.resetAllStrats()
      self.signalStratBtn.setChecked(True)
      self.mainModel.mktStrategy = Strategies.Signal()




