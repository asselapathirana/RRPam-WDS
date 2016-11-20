import os
import sys
import time
import unittest

#from guiqwt import tests
#from guiqwt.plot import CurveDialog
#from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication
#from PyQt4.QtTest import QTest

#from rrpam_wds.gui.dialogs import MainWindow


class mdi_graph_test(unittest.TestCase):
    start=0
    stop=0    

    def setUp(self):
        global start
        self.app=QApplication(sys.argv)        
        start=time.time()
        #self.aw = MainWindow()
        #self.aw.setWindowTitle("Testing multi document window") 
        pass
    def tearDown(self):
        global stop
        stop=time.time()
        print("\ncalculation took %0.2f seconds." % (stop-start))
        pass    
    
   # def test_just_graph_in_mdi(self):
   #     self.graph=CurveDialog(wintitle="guiqwt plot", icon="guiqwt.svg", 
   #                           edit=False, 
   #                           toolbar=True, 
   #                           options=None, 
   #                           parent=self.aw, 
   #                           panels=None)
   #     
   #     self.aw.addSubWindow(self.graph)
        
   # def runTest(self): 
   #     """ otherwise python 2.7 returns an error 
   #     ValueError: no such test method in <class 'myapp.tests.SessionTestCase'>: runTest"""
   #    pass
   
    def test_dummy(self):
        pass
       
    
def drive(test=True): # pragma: no cover
    if(test):
        unittest.main(verbosity=2) 
    else:
        ot=mdi_graph_test()
        ot.setUp()
        ot.test_just_graph_in_mdi()
        ot.aw.show()
        sys.exit(ot.app.exec_())
        
if __name__ == '__main__':  # pragma: no cover
    drive(True)
