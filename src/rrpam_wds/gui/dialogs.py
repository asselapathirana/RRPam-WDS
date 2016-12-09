from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA

import random
import sys
import math

from guidata.configtools import add_image_module_path
from guiqwt.builder import make
from guiqwt.config import CONF
from guiqwt.plot import CurveDialog
from guiqwt.styles import style_generator
from guiqwt.styles import update_style_attr
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from numpy import arange
from numpy import interp
from numpy import linspace
from numpy import pi
from numpy import sin
from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMdiArea
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QVBoxLayout

import rrpam_wds.gui.utils as u
from rrpam_wds.constants import curve_colors
from rrpam_wds.constants import units
from rrpam_wds.gui import monkey_patch_guiqwt_guidata
from rrpam_wds.gui.custom_toolbar_items import ResetZoomTool

# there are some changes to the guiqwt classes to be done. It is not easy to do this by subclassing, as
# we need to user make.* facotry
monkey_patch_guiqwt_guidata._patch_all()
# show guiqwt where the images are.
add_image_module_path("rrpam_wds.gui", "images")
# this how we change an option
CONF.set("plot", "selection/distance", 10.0)
# todo: This has to be saved as project's setting file (CONF.save provides that facility)

STYLE = style_generator()


class CurveDialogWithClosable(CurveDialog):

    """The mother dialog from which all the graph windows inherit from
       The constructor can send 'options' keyward argument containing a dict. Following entries are
       possible
                 title=None,
                 xlabel=None, ylabel=None, xunit=None, yunit=None,
                 section="plot", show_itemlist=False, gridparam=None,
                 curve_antialiasing=None


    """

    def __init__(self, *args, **kwargs):
        super(CurveDialogWithClosable, self).__init__(*args, **kwargs)
        self._can_be_closed = True
        self.get_plot().set_antialiasing(True)
        self.add_tools()

    def set_all_private(self):
        """" Set all current items in the plot private"""
        [x.set_private(True) for x in self.get_plot().get_items()]

    def set_axes_limits(self, axes_limits=None):
        """Sets axes limits axes_limits should be a list with four float values [x0,x1,y0,y1] """
        self.get_plot().PREFERRED_AXES_LIMITS = axes_limits
        # now autoscale
        self.get_plot().do_autoscale()

    def add_tools(self):
        """adds the custom tools necessary"""
        self.add_tool(ResetZoomTool)

    def setClosable(self, closable=True):
        self._can_be_closed = closable

    def closeEvent(self, evnt):
        if self._can_be_closed:
            super(CurveDialogWithClosable, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.setWindowState(QtCore.Qt.WindowMinimized)

    def keyPressEvent(self, e):
        if (e.key() != QtCore.Qt.Key_Escape):
            super(CurveDialogWithClosable, self).keyPressEvent(e)
        else:
            pass


class RiskMatrix(CurveDialogWithClosable):
    SCALE = 10.

    def __init__(self, name="Risk Matrix", parent=None, units=units["EURO"], options={}, axes_limits=[0, 15000, 0, 100]):
        if("xlabel" not in options):
            options['xlabel'] = "Consequence (%s)" %(units)
        if("ylabel" not in options):
            options['ylabel'] = "Proabability(-)"
        if("gridparam" not in options):
            options['gridparam'] = make.gridparam()

        super(RiskMatrix, self).__init__(edit=False,
                                         icon="risk.svg",
                                         toolbar=True,
                                         options=options,
                                         parent=parent,
                                         panels=None,
                                         wintitle=name)
        self.setClosable(False)
        _axes_limits=axes_limits[0],axes_limits[1]*1.1,axes_limits[2],axes_limits[3]*1.1
        self.set_axes_limits(_axes_limits)
        
        l=make.legend("TR")
        self.get_plot().add_item(l)        
        self.set_all_private()

    def get_ellipse_xaxis(self,consequence, probability):
        l=self.get_plot().PREFERRED_AXES_LIMITS
        SCALE = self.get_scale(consequence, probability, l)
        return consequence - SCALE, probability + SCALE,\
               consequence + SCALE, probability - SCALE       

    def get_scale(self, consequence, probability, l):
        SCALE=self.SCALE*math.pow(consequence*probability,.25)/math.pow((l[1]*l[3]),.25)
        return SCALE
    
    def get_proper_axis_limits(self):
        return 

    def plot_item(self, consequence, probability, title="Point"):
        global STYLE
        ci = make.ellipse(*self.get_ellipse_xaxis(consequence, probability) ,
                          title=title)

        ci.shapeparam._DataSet__icon = u.get_icon('Risk')
        ci.shapeparam._DataSet__title = title
        param = ci.shapeparam
        param.fill.color = QColor('red')
        param.sel_fill.color = QColor('purple')
        param.sel_fill.alpha = .7
        param.sel_symbol.Marker="NoSymbol"
        param.sel_symbol.Color=QColor('red')
        update_style_attr('-r', param)
        param.update_shape(ci)
        self.get_plot().add_item(ci)
        # now add a label with title
        ci
        la = make.label(title, ci.get_center(), (0, 0), "C")
        


class NetworkMap(CurveDialogWithClosable):

    def __init__(self, name="Network Map", nodes=None, links=None, parent=None, options={}):
        pass
        if("xlabel" not in options):
            options['xlabel'] = "X (distance units)"
        if("ylabel" not in options):
            options['ylabel'] = "Y (distance units)"

        gridparam = make.gridparam()

        super(NetworkMap, self).__init__(edit=False,
                                         icon="network.svg",
                                         toolbar=True,
                                         options=dict(gridparam=gridparam),
                                         parent=parent,
                                         wintitle=name,
                                         panels=None)
        self.setClosable(False)
        
        # legend = make.legend("TR")
        # self.get_plot().add_item(legend)
        self.set_all_private()
        if(nodes):
            self.draw_nodes(nodes)

        # we don't want users to select grid, or nodes and they should not appear in the item list.
        # So lock'em up.
        self.set_all_private()

        if(links):
            self.draw_links(links)
        self.get_plot().do_autoscale(replot=True)

    def interp_curve(self, x, y):
        # how many points in the line (say max is 5)
        DELTA = .01
        t = arange(len(x))
        t_ = arange(0, len(x) - 1 + DELTA, DELTA)
        x_ = interp(t_, t, x)
        y_ = interp(t_, t, y)

        return x_, y_

    def draw_links(self, links):
        for link in links:
            pts = [(link.start.x, link.start.y)] + link.vertices + [(link.end.x, link.end.y)]
            x = [n[0] for n in pts]
            y = [n[1] for n in pts]
            x_, y_ = self.interp_curve(x, y)
            cu = make.curve(x_, y_, title=u.get_title(link))
            cu.curveparam._DataSet__icon = u.get_icon(link)
            cu.curveparam._DataSet__title = u.get_title(link)
            self.get_plot().add_item(cu)

            # create a label for the node and add it to the plot
            l = int(len(x_) / 2.0)
            la = make.label(link.id, (x_[l], y_[l]), (0, 0), "C")
            la.set_private(True)
            self.get_plot().add_item(la)

    def draw_nodes(self, nodes):

        for node in nodes:
            cu = make.curve([node.x, node.x], [node.y, node.y],
                            # ^ this is a hack. gwiqwt curve has problems when constructed with single coordinae
                            title=u.get_title(node), marker="Ellipse", curvestyle="NoCurve")
            cu.set_selectable(False)
            cu.set_private(True)
            # pt=make.ellipse(node.x-.1,node.y-.1,node.x+.1,node.y+.1)
            # pt=PointShape(x=node.x,y=node.y, color="g")
            cu.curveparam._DataSet__icon = u.get_icon(node)
            cu.curveparam._DataSet__title = u.get_title(node)
            self.get_plot().add_item(cu)

            # create a label for the node and add it to the plot
            la = make.label(node.id, (node.x, node.y), (0, 0), "TL")
            la.set_private(True)
            self.get_plot().add_item(la)


class optimalTimeGraph(CurveDialogWithClosable):

    def __init__(self, name="Whole life cost", mainwindow=None, year=None, damagecost=None, renewalcost=None,
                 units=units["EURO"], parent=None, options={}):
        self.mainwindow=mainwindow
        if("xlabel" not in options):
            options['xlabel'] = "Time(years)"
        if("ylabel" not in options):
            options['ylabel'] = "Cost (%s)" % (units)

        self.curvesets = []

        super(optimalTimeGraph, self).__init__(edit=False,
                                               icon="wlc.svg",
                                               toolbar=True,
                                               options=options,
                                               parent=parent,
                                               panels=None,
                                               wintitle=name)
        if (isinstance(self.mainwindow,MainWindow)):
            self.mainwindow.optimaltimegraphs[id(self)]=self
        
        legend = make.legend("TR")
        self.get_plot().add_item(legend)
        if(year is None or damagecost is None or renewalcost is None):
            pass
        else:
            self.plotCurveSet(name, year, damagecost, renewalcost)
            
    def closeEvent(self, evnt):
        if (not isinstance(self.mainwindow,MainWindow)):
            _can_be_closed=True
        elif (len(self.mainwindow.optimaltimegraphs) > 1):
            _can_be_closed=True
            del(self.mainwindow.optimaltimegraphs[id(self)])
        else:
            _can_be_closed=False
            
        if _can_be_closed:
            super(CurveDialogWithClosable, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.setWindowState(QtCore.Qt.WindowMinimized)    

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
    optimaltimegraphs={}
    class emptyclass: pass
    menuitems=emptyclass
    menuitems.new_wlc = "New WLC window"
    menuitems.cascade ="Cascade"
    menuitems.tiled  ="Tiled"

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        self.setMenu()
        self.standard_windows()
        
    def standard_windows(self):
        self.add_networkmap()
        self.add_riskmatrix()
        self.add_optimaltimegraph()
            
    def add_optimaltimegraph(self):
        wlc=optimalTimeGraph(mainwindow=self)
        self.mdi.addSubWindow(wlc)
        wlc.show()
        

    def add_riskmatrix(self):
        if(not any([x for x in self.mdi.subWindowList() if isinstance(x.widget(),RiskMatrix)])):
            self.riskmatrix=RiskMatrix()
            self.mdi.addSubWindow(self.riskmatrix)
            self.riskmatrix.show()

    def add_networkmap(self):
        if(not any([x for x in self.mdi.subWindowList() if isinstance(x.widget(),NetworkMap)])):
                    self.networkmap=NetworkMap("Network Map")
                    self.mdi.addSubWindow(self.networkmap)
                    self.networkmap.show()        

    def setMenu(self):
        bar = self.menuBar()

        file = bar.addMenu("File")
        file.addAction(self.menuitems.new_wlc)
        file.triggered[QAction].connect(self.windowaction)
        file2 = bar.addMenu("View")
        file2.addAction(self.menuitems.cascade)
        file2.addAction(self.menuitems.tiled)
        file2.triggered[QAction].connect(self.windowaction)
        self.setWindowTitle("MDI demo")

    def windowaction(self, q):
        print("triggered")

        if q.text() == self.menuitems.new_wlc:
            self.add_optimaltimegraph()

        if q.text() == "New matplotlib":
            MainWindow.count = MainWindow.count + 1
            self.new_matplotlib_window()

        if q.text() == self.menuitems.cascade:
            self.mdi.cascadeSubWindows()

        if q.text() == self.menuitems.tiled:
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
        return win

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
