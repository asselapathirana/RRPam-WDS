from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA
import sys
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
import os

from rrpam_wds.cli import Main
from rrpam_wds.gui.dialogs import MainWindow

from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import time
from rrpam_wds.gui.dialogs import MainWindow


class Tester(QObject):
    finished = pyqtSignal()
    addAWindow = pyqtSignal(int)
    timetogo = pyqtSignal()
    
    def __init__(self, mainwindow):
        self.mainwindow=mainwindow
        super(Tester, self).__init__()
        
    
    @pyqtSlot()
    def do_some_testing(self): # A slot takes no params
        for i in range(1, 11):
            time.sleep(1)
            self.addAWindow.emit(i)
            print(i)
            
        self.finished.emit()
        time.sleep(.1)  # this is a hack. If this is not here, the main (gui) thread will freeze. Need to find why. 
        self.now_wait()

    @pyqtSlot()
    def now_wait(self):
        print("Work done .. now biding time")
        for i in range(1,11):
            time.sleep(1)
            print(11-i)
        print (".. and done!")
        time.sleep(.1)
        QApplication.processEvents()
        if(not len(self.mainwindow.mdi.subWindowList())==10):
            raise Exception        
        self.timetogo.emit()

def set_paths(sys, os):
    if (getattr(sys, 'frozen', False)):
        print("I am frozen")
        print("I need the platform library files in the same directory with me!")
        print ("(on windows there are at Library/plugins/platforms on POSIXes plugin/platforms)")
        p=os.path.dirname(sys.executable)
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = p
        sys.path.append(p)
    else:
        print("I am not frozen!")
        print("If you get platform plugin not found error you may have to point QT_QPA_PLATFORM_PLUGIN_PATH to platforms directory ")
        print ("(on windows there are at Library/plugins/platforms on POSIXes plugin/platforms)")
        

set_paths(sys, os)

if (len(sys.argv) == 1):  # plain run
    main=main()
    sys.exit(main.app.exec_())
        
else: # run as a test. Open, run tests and close. 
    main=Main()
    tester=Tester(main.win)
    thread=QThread()
    tester.moveToThread(thread)
    tester.addAWindow.connect(main.win.new_window)
    #tester.timetogo.connect(thread.quit)
    tester.finished.connect(thread.quit) # this is also needed to prevent gui from freezing upon finishing the thread. 
    thread.started.connect(tester.do_some_testing)
    tester.timetogo.connect(main.app.exit)
    thread.start()
    main.show_application()
 

    
    
       
    
    
    

