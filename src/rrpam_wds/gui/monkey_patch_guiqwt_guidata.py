# -*- coding: utf-8 -*-
import logging

import numpy as np
from guidata.py3compat import maxsize
from guiqwt.curve import CurveItem
from guiqwt.curve import CurvePlot
from guiqwt.curve import ItemListWidget
from guiqwt.curve import get_icon
from guiqwt.curve import seg_dist
from PyQt5.QtCore import QPointF


# from rrpam_wds.gui.utils import table_editor


def _patch_all():
    _patch_item_list()
    _patch_curve_do_autoscale()
    _patch_curveitem_hit_test()
    _patch_curveplot___del__()
    # _patch_floatarraywidget_edit_array()


# def _patch_floatarraywidget_edit_array():
# no need to # save the original
# orig_edit_array = FloatArrayWidget.edit_array
#
# def custom_edit_array(self):
# """Open an array editor dialog"""
# parent = self.parent_layout.parent
# label = self.item.get_prop_value("display", "label")
# editor = arrayeditor.ArrayEditor(parent)
#
# ret = table_editor(self.parent_layout.parent, self.arr)
# if (ret):
# self.update(self.arr)
#
# now monkey-patch
# FloatArrayWidget.edit_array = custom_edit_array


def _patch_curveplot___del__():
    """1. Close a subwindow within qmidarea. 2. Close the application
    It crashes with the message:
    Traceback (most recent call last):
  File "/home/user/miniconda3/envs/py34/lib/python3.5/site-packages/guiqwt/curve.py", line 1404, in __del__
    canvas.removeEventFilter(self.filter)
RuntimeError: wrapped C/C++ object of type QwtPlotCanvas has been deleted

    Currently I assume this is a bug in the curve.__del__ routine, not an issure of my implementation.
    So, just adding a try: except clause
    """
    orig___del__ = CurvePlot.__del__

    def custom__del__(self):
        try:
            orig___del__(self)
        except:
            logger = logging.getLogger()
            logger.info("Better to fix me later.")

    # now monkey patch
    CurvePlot.__del__ = custom__del__


def _patch_curveitem_hit_test():
    # we are not using the original method, we completely rewrite it.
    # orig_hit_test = CurveItem.hit_test  # save the original method

    def custom_hit_test(self, pos):
        """Calcul de la distance d'un point à une courbe
        renvoie (dist, handle, inside)"""
        if self.is_empty():
            return maxsize, 0, False, None
        plot = self.plot()
        ax = self.xAxis()
        ay = self.yAxis()
        px = plot.invTransform(ax, pos.x())
        py = plot.invTransform(ay, pos.y())

        tmpx = self._x - px
        tmpy = self._y - py
        if np.count_nonzero(tmpx) != len(tmpx) or\
           np.count_nonzero(tmpy) != len(tmpy):
            # Avoid dividing by zero warning when computing dx or dy
            return maxsize, 0, False, None
        tmpx = tmpx * tmpx
        tmpy = tmpy * tmpy

        v = tmpx * tmpx + tmpy * tmpy
        i = v.argmin()

        # Recalcule la distance dans le répère du widget
        p0x = plot.transform(ax, self._x[i])
        p0y = plot.transform(ay, self._y[i])
        if i + 1 >= self._x.shape[0]:
            p1x = p0x
            p1y = p0y
        else:
            p1x = plot.transform(ax, self._x[i + 1])
            p1y = plot.transform(ay, self._y[i + 1])
        distance = seg_dist(QPointF(pos), QPointF(p0x, p0y), QPointF(p1x, p1y))
        return distance, i, False, None

    # now monkey patch
    CurveItem.hit_test = custom_hit_test


def _patch_item_list():
    orig___get_item_icon = ItemListWidget._ItemListWidget__get_item_icon  # save the original method

    def custom_get_item_icon(self, item):
        try:
            icon_name = item.curveparam._DataSet__icon
            return get_icon(icon_name)
        except AttributeError:
            return orig___get_item_icon(self, item)

    # now monkey patch
    ItemListWidget._ItemListWidget__get_item_icon = custom_get_item_icon


def _patch_curve_do_autoscale():
    orig_do_autoscale = CurvePlot.do_autoscale  # save the original method

    def custom_do_autoscale(self, replot=True, axis_id=None):
        try:
            ax = self.get_axis_id('bottom')
            self.set_axis_limits(ax, self.PREFERRED_AXES_LIMITS[0], self.PREFERRED_AXES_LIMITS[1])
            ay = self.get_axis_id('left')
            self.set_axis_limits(ay, self.PREFERRED_AXES_LIMITS[2], self.PREFERRED_AXES_LIMITS[3])
        except:
            auto = self.autoReplot()
            self.setAutoReplot(False)
            # ---------------------------
            # now first call the original do_autoscale_method
            orig_do_autoscale(self)
            # then take axis limits and add a bit.
            for axis_id in self.AXIS_IDS if axis_id is None else [axis_id]:
                vmin, vmax = self.get_axis_limits(axis_id)
                dv = vmax - vmin
                vmin -= .1 * dv
                vmax += .1 * dv
                self.set_axis_limits(axis_id, vmin, vmax)
            # --------------------------
            self.setAutoReplot(auto)
            if replot:
                self.replot()
            self.SIG_PLOT_AXIS_CHANGED.emit(self)
    # now monkey patch
    CurvePlot.do_autoscale = custom_do_autoscale
