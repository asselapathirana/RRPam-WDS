from guiqwt.curve import CurvePlot
from guiqwt.curve import ItemListWidget
from guiqwt.curve import get_icon


def _patch_all():
    _patch_item_list()
    _patch_curve_do_autoscale()


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
