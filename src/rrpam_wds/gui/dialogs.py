import sys

from guiqwt.builder import make
from guiqwt.plot import CurveDialog
from numpy import linspace
from numpy import sin
from PyQt4 import QtCore
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QMdiArea


class MyCurveDialog(CurveDialog):

    def __init__(self, *args, **kwargs):
        super(MyCurveDialog, self).__init__(*args, **kwargs)
        self._can_be_closed = True

    def setClosable(self, closable=True):
        self._can_be_closed = closable

    def closeEvent(self, evnt):
        if self._can_be_closed:
            super(MyCurveDialog, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.setWindowState(QtCore.Qt.WindowMinimized)


class MainWindow(QMainWindow):
    count = 0

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        self.setMenu()
        self.new_window(closable=False)

    def setMenu(self):
        bar = self.menuBar()

        file = bar.addMenu("File")
        file.addAction("New")
        file.triggered[QAction].connect(self.windowaction)
        file2 = bar.addMenu("View")
        file2.addAction("cascade")
        file2.addAction("Tiled")
        file2.triggered[QAction].connect(self.windowaction)
        self.setWindowTitle("MDI demo")

    def windowaction(self, q):
        print("triggered by :", self.sender().title())

        if q.text() == "New":
            MainWindow.count = MainWindow.count + 1

            self.new_window()

        if q.text() == "cascade":
            self.mdi.cascadeSubWindows()

        if q.text() == "Tiled":
            self.mdi.tileSubWindows()

    def addSubWindow(self, *args, **kwargs):
        self.mdi.addSubWindow(*args, **kwargs)

    def new_window(self, closable=True):
        win = MyCurveDialog(
            edit=False, toolbar=True, wintitle="CurveDialog test",
            options=dict(title="Title", xlabel="xlabel", ylabel="ylabel"))
        win.setClosable(closable)
        self.plot_some_junk(win)

        win.setWindowTitle("subwindow" + str(MainWindow.count))
        self.mdi.addSubWindow(win)
        win.show()

    def plot_some_junk(self, win):
        plot = win.get_plot()
        x2 = linspace(-10, 10, 20)
        y2 = sin(sin(sin(x2)))
        curve2 = make.curve(x2, y2, color="g", curvestyle="Sticks")
        curve2.setTitle("toto")
        plot.add_item(curve2)

        # if q.text() == "graph"


def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
