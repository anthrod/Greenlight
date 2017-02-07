from Sight.Control import MainControl as mc
from PyQt4.QtGui import *
import sys
import os

def main():
  print('Go ahead...I won\'t bite')
  datadir = '/home/anthrod/Workspace/scratch/GreenWick/data'

  app = QApplication(sys.argv)

  #Create the controller, which will instantiate the MVC chain
  controller = mc.MainControl(width=1400, height=100)

  sys.exit(app.exec_())
  
  

if __name__ == '__main__':
  main()
