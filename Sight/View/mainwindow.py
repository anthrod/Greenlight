import sys
from PyQt4.QtGui import *
from Control import maincontroller as mc
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import pandas as pd


class mainwindow(QWidget):

  def __init__(self, width=800, height=600, args=[]):   
    #QMainWindow.__init__(self)
    QWidget.__init__(self)
    self.resize(width, height)
    self.setWindowTitle('The Void')

    defaultLoadFile = '/home/anthrod/Workspace/scratch/GreenWick/data/GSPC/gspc-daily-nodivs-1960-2016.csv'
    self.loadFileText = defaultLoadFile

    self.controller = mc.MainController()
    
    self.grid = QGridLayout()
    self.setLayout(self.grid)
    self.setGeometry(width, height, width, height)
    self.setWindowTitle('Greenlight')
  
    row = 1

    ########################TEXT OUTPUT#########################

    self.statusTextField = QLineEdit(self)
    self.statusTextField.setReadOnly(True)
    self.statusTextField.setText('Step into the Greenlight...')
    self.grid.addWidget(self.statusTextField, row, 1, 1, 3)
   
    ####################LOAD FROM TICKER########################   

    row=row+1
    self.ticker = 'GSPC'
    self.pullTickerTextField = QLineEdit(self)
    self.pullTickerTextField.textChanged.connect(self.pullTickerTextChanged)
    self.pullTickerTextField.setText(self.ticker)
    self.grid.addWidget(self.pullTickerTextField, row, 1, 1, 2)

    self.pullTickerBtn = QPushButton('Pull', self)
    self.pullTickerBtn.clicked.connect(self.pullTickerBtnPressed)
    self.grid.addWidget(self.pullTickerBtn, row, 3, 1, 1)

    ####################LOAD FROM CSV############################

    row=row+1
    self.loadFileTextField = QLineEdit(self)
    self.loadFileTextField.textChanged.connect(self.loadFileTextChanged)
    self.loadFileTextField.setText(defaultLoadFile)
    self.grid.addWidget(self.loadFileTextField, row, 1, 1, 2)

    self.loadFileBtn = QPushButton('Load', self)
    self.loadFileBtn.clicked.connect(self.loadFileBtnPressed)
    self.grid.addWidget(self.loadFileBtn, row, 3, 1, 1)

    ###############SIMPLE MOVING AVERAGE########################

    row=row+1
    self.movingAvgDaysField = QLineEdit(self)
    self.movingAvgDaysField.textChanged.connect(self.movingAvgTextChanged)
    self.movingAvgDaysField.setText('10')
    self.grid.addWidget(self.movingAvgDaysField, row, 2, 1, 1)
    self.movingAvgNumDays = 10

    self.trendLineBtn = QPushButton('SMA', self)
    self.trendLineBtn.clicked.connect(self.trendLineBtnPressed)
    self.grid.addWidget(self.trendLineBtn, row, 3, 1, 1)

    #############EXPONENTIAL MOVING AVERAGE####################
 
    row=row+1
    self.emaDaysField = QLineEdit(self)
    self.emaDaysField.textChanged.connect(self.emaTextChanged)
    self.emaDaysField.setText('12')
    self.grid.addWidget(self.emaDaysField, row, 2, 1, 1)
    self.emaNumDays = 12

    self.emaLineBtn = QPushButton('EMA', self)
    self.emaLineBtn.clicked.connect(self.emaLineBtnPressed)
    self.grid.addWidget(self.emaLineBtn, row, 3, 1, 1)

    ##################BOLLINGER BANDS##########################
 
    row=row+1
    self.bollingerField = QLineEdit(self)
    self.bollingerField.textChanged.connect(self.bollingerChanged)
    self.bollingerField.setText('30')
    self.grid.addWidget(self.bollingerField, row, 2, 1, 1)
    self.bollingerLength = 30
    self.controller.setBollingerLength(self.bollingerLength)

    self.bollingerBtn = QPushButton('Bollinger', self)
    self.bollingerBtn.clicked.connect(self.bollingerBtnPressed)
    self.grid.addWidget(self.bollingerBtn, row, 3, 1, 1)

    ########################START DATE##########################

    row=row+1
    self.startYearField = QLineEdit(self)
    self.startYearField.textChanged.connect(self.startYearChanged)
    self.startYearField.setText('1700')
    self.grid.addWidget(self.startYearField, row,1)
    self.startYear = 0

    self.startMonthField = QLineEdit(self)
    self.startMonthField.textChanged.connect(self.startMonthChanged)
    self.startMonthField.setText('01')
    self.grid.addWidget(self.startMonthField, row,2)
    self.startMonth = 0

    self.startDayField = QLineEdit(self)
    self.startDayField.textChanged.connect(self.startDayChanged)
    self.startDayField.setText('01')
    self.grid.addWidget(self.startDayField, row,3)
    self.startDay = 0

    ##########################END DATE#############################

    row=row+1
    self.endYearField = QLineEdit(self)
    self.endYearField.textChanged.connect(self.endYearChanged)
    self.endYearField.setText('3000')
    self.grid.addWidget(self.endYearField, row,1)
    self.endYear = 3000

    self.endMonthField = QLineEdit(self)
    self.endMonthField.textChanged.connect(self.endMonthChanged)
    self.endMonthField.setText('12')
    self.grid.addWidget(self.endMonthField, row,2)
    self.endMonth = 99

    self.endDayField = QLineEdit(self)
    self.endDayField.textChanged.connect(self.endDayChanged)
    self.endDayField.setText('30')
    self.grid.addWidget(self.endDayField, row,3)
    self.endDay = 99

    ########################REFRESH PLOT############################

    row=row+1
    self.replotBtn = QPushButton('Replot', self)
    self.replotBtn.clicked.connect(self.replotBtnPressed)
    self.grid.addWidget(self.replotBtn, row, 2)

    self.show()

  ######################GUI FUNCTIONS#########################

  def pullTickerTextChanged(self, text):
    self.ticker = text

  def pullTickerBtnPressed(self):
    self.statusTextField.setText('Pulling data for ' + self.ticker + '...')
    if self.controller.pullTicker(str(self.ticker)) is True:
      self.statusTextField.setText(self.ticker + ' data loaded.')

  def loadFileBtnPressed(self):
    self.controller.loadFile(self.loadFileText)
    self.statusTextField.setText('Data loaded from file')

  def loadFileTextChanged(self, text):
    self.loadFileText = text

  def trendLineBtnPressed(self):
    self.controller.addSimpMovingAvg(self.movingAvgNumDays)

  def bollingerChanged(self, text):
    self.bollingerLength = int(text)

  def bollingerBtnPressed(self):
    self.controller.toggleBollinger()

  def movingAvgTextChanged(self, text):
    self.movingAvgNumDays = int(text)

  def emaLineBtnPressed(self):
    self.controller.addExpMovingAvg(self.emaNumDays)

  def emaTextChanged(self, text):
    self.emaNumDays = int(text)

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
    self.controller.reDate(
                             startDay   = self.startDay,
                             startMonth = self.startMonth,
                             startYear  = self.startYear,
                             endDay     = self.endDay,
                             endMonth   = self.endMonth,
                             endYear    = self.endYear    )







