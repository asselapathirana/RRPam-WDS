import logging

# from guidata.configtools import IMG_PATH
from guiqwt import tools


class ResetZoomTool(tools.CommandTool):
    TITLE = "Reset zoom"
    ICON = "resetzoom.png"

    def __init__(self, manager, toolbar_id=tools.DefaultToolbarID):

        super(ResetZoomTool, self).__init__(manager, self.TITLE, icon=self.ICON,
                                            toolbar_id=toolbar_id)

    def activate_command(self, plot, checked):
        """Activate tool"""
        logger = logging.getLogger()
        logger.info("Reset scale")
        plot.do_autoscale()


class PlotWLCTool(tools.CommandTool):
    TITLE = "Plot WLC curves for selected assets"
    ICON = "wlc.png"

    def __init__(self, manager, toolbar_id=tools.DefaultToolbarID):

        super(PlotWLCTool, self).__init__(manager, self.TITLE, icon=self.ICON,
                                          toolbar_id=toolbar_id)

    def activate_command(self, plot, checked):
        """Activate tool"""
        logger = logging.getLogger()
        logger.info("Plot WLC")
        plot.manager._plot_selected_items()
