"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mrrpam_wds` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``rrpam_wds.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``rrpam_wds.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA

import argparse
import sys
import os

from PyQt5.QtCore import QObject, QTimer
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMessageBox

from rrpam_wds.gui.dialogs import MainWindow

parser = argparse.ArgumentParser(description='Command description.')
parser.add_argument('names', metavar='NAME', nargs=argparse.ZERO_OR_MORE,
                    help="A name of something.")


class Main(QObject):

    def __init__(self, args=None):
        args = parser.parse_args(args=args)
        print(args.names)
        self.app = QApplication([])
        self.win = MainWindow()
        self.win.show()
        super(Main, self).__init__()

    @pyqtSlot()
    def show_application(self):
        sys.exit(self.app.exec_())

    #@pyqtSlot(str)
    #def screenshot(self, filename):
        #if (getattr(sys, 'frozen', False)):
            #p = os.path.dirname(sys.executable)
        #else:
            #p = os.getcwd()
            
        #filename=os.path.join(p,filename)
        #msg = QMessageBox()
        #msg.setIcon(QMessageBox.Information)
        #msg.setText("Screenshot will be saved at : %s" % (filename)) 
        #QTimer.singleShot(5000, msg.accept)
        #msg.exec_()
        
        
        
        # now take a screenshot
        qs = QApplication.primaryScreen()
        if (qs):
            qs.grabWindow(self.win.winId()).save(filename, 'jpg')
        else:
            QPixmap().save(filename, 'jpg')
