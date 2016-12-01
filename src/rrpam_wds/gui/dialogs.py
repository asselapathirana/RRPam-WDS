from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA

import random
import sys

from guiqwt.builder import make
from guiqwt.plot import CurveDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from numpy import arange
from numpy import linspace
from numpy import pi
from numpy import sin
from PyQt5 import QtCore
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMdiArea
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QVBoxLayout

from rrpam_wds.constants import curve_colors
from rrpam_wds.constants import units


class CurveDialogWithClosable(CurveDialog):

    """"The mother dialog from which all the graph windows inherit from"""

    def __init__(self, *args, **kwargs):
        super(CurveDialogWithClosable, self).__init__(*args, **kwargs)
        self._can_be_closed = True
        self.get_plot().set_antialiasing(True)

    def setClosable(self, closable=True):
        self._can_be_closed = closable

    def closeEvent(self, evnt):
        if self._can_be_closed:
            super(CurveDialogWithClosable, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.setWindowState(QtCore.Qt.WindowMinimized)


class optimalTimeGraph(CurveDialogWithClosable):

    def __init__(self, name, year, damagecost, renewalcost,
                 units=units["EURO"], parent=None, options={}):
        if("xlabel" not in options):
            options['xlabel'] = "Time(years)"
        if("ylabel" not in options):
            options['ylabel'] = "Cost (%s)" % (units)

        # if("wintitle" not in options):
        #     options['wintitle'] = "Costs against time"

        self.curvesets = []

        super(optimalTimeGraph, self).__init__(edit=False,
                                               icon="guiqwt.svg",
                                               toolbar=True,
                                               options=options,
                                               parent=parent,
                                               panels=None)
        legend = make.legend("TR")
        self.get_plot().add_item(legend)
        if(year is None or damagecost is None or renewalcost is None):
            pass
        else:
            self.plotCurveSet(name, year, damagecost, renewalcost)

    def plotCurveSet(self, name, year, damagecost, renewalcost):
        c = curve_colors[len(self.curvesets) % len(curve_colors)]
        dc = make.curve(
            year, damagecost, title="Damage Cost", color=c, linestyle="DashLine",
            linewidth=3, marker=None,
            markersize=None,
            markerfacecolor=None,
            markeredgecolor=None, shade=None,
            curvestyle=None, baseline=None,
            xaxis="bottom", yaxis="left")
        self.get_plot().add_item(dc)
        rc = make.curve(
            year, renewalcost, title="Renewal Cost", color=c, linestyle="DotLine",
            linewidth=3, marker=None,
            markersize=None,
            markerfacecolor=None,
            markeredgecolor=None, shade=None,
            curvestyle=None, baseline=None,
            xaxis="bottom", yaxis="left")
        self.get_plot().add_item(rc)
        tc = make.curve(
            year, damagecost + renewalcost, title="Total Cost", color=c, linestyle=None,
            linewidth=5, marker=None,
            markersize=None,
            markerfacecolor=None,
            markeredgecolor=None, shade=None,
            curvestyle="Lines", baseline=None,
            xaxis="bottom", yaxis="left")
        self.get_plot().add_item(tc)
        self.curvesets.append([name, dc, tc, rc])


class MainWindow(QMainWindow):

    """The maion 'container' of the application. This is a multi-document interface where all other
    windows live in."""
    count = 0

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        self.setMenu()
        # self.new_window(closable=False)

    def setMenu(self):
        bar = self.menuBar()

        file = bar.addMenu("File")
        file.addAction("New guiqwt")
        file.addAction("New matplotlib")
        file.triggered[QAction].connect(self.windowaction)
        file2 = bar.addMenu("View")
        file2.addAction("cascade")
        file2.addAction("Tiled")
        file2.triggered[QAction].connect(self.windowaction)
        self.setWindowTitle("MDI demo")

    def windowaction(self, q):
        print("triggered")

        if q.text() == "New guiqwt":
            MainWindow.count = MainWindow.count + 1
            # sub = QDialog()
            # sub.setWidget(QTextEdit())

            self.new_window()

        if q.text() == "New matplotlib":
            MainWindow.count = MainWindow.count + 1
            self.new_matplotlib_window()

        if q.text() == "cascade":
            self.mdi.cascadeSubWindows()

        if q.text() == "Tiled":
            self.mdi.tileSubWindows()

    def addSubWindow(self, *args, **kwargs):
        self.mdi.addSubWindow(*args, **kwargs)

    def new_window(self, closable=True):
        win = CurveDialogWithClosable(
            edit=False, toolbar=True, wintitle="CurveDialog test",
            options=dict(title="Title", xlabel="xlabel", ylabel="ylabel"))
        win.setClosable(closable)
        self.plot_some_junk(win)

        win.setWindowTitle("subwindow" + str(MainWindow.count))
        self.mdi.addSubWindow(win)
        win.show()

    def new_matplotlib_window(self, closable=True):
        win = MatplotlibDialog()
        # win.setClosable(closable)
        # self.plot_some_junk(win)

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


class MatplotlibDialog(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        # self.main_widget = QWidget(self)

        l = QVBoxLayout(self)
        sc = MyStaticMplCanvas(self, width=5, height=2, dpi=100)
        navi_toolbar = NavigationToolbar(sc, self)
        dc = MyDynamicMplCanvas(self, width=5, height=2, dpi=100)
        navi_toolbar2 = NavigationToolbar(dc, self)
        l.addWidget(sc)
        l.addWidget(navi_toolbar)
        l.addWidget(dc)
        l.addWidget(navi_toolbar2)

        # self.main_widget.setFocus()
        self.resize(self.sizeHint())
        # self.setCentralWidget(self.main_widget)
        # self.statusBar().showMessage("All hail matplotlib!", 2000)


class MyMplCanvas(FigureCanvas):

    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):

    """Simple canvas with a sine plot."""

    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        self.axes.plot(t, s)


class MyDynamicMplCanvas(MyMplCanvas):

    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [random.randint(0, 10) for i in range(4)]

        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()


def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    mpl = MatplotlibDialog()
    ex.addSubWindow(mpl)
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
