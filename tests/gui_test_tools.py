
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QMdiArea


class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        self.main_widget = None
        
        
class MDIWindow(ApplicationWindow):
    
    def __init__(self, parent=None):
        ApplicationWindow.__init__(self)
        self.main_widget=QMdiArea(parent)
        self.setCentralWidget(self.main_widget)
    

        