import numpy as np
from guidata.py3compat import maxsize
from guiqwt.curve import CurveItem
from guiqwt.curve import CurvePlot
from guiqwt.curve import ItemListWidget
from guiqwt.curve import get_icon
from guiqwt.curve import seg_dist
from PyQt5.QtCore import QPointF


def _patch_all():
    _patch_item_list()
    _patch_curve_do_autoscale()
    _patch_curveitem_hit_test()


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
            orig_do_autoscale(self)
    # now monkey patch
    CurvePlot.do_autoscale = custom_do_autoscale
