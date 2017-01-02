import logging
import os
import sys

# from guidata.configtools import IMG_PATH
from guiqwt import tools

if getattr(sys, 'frozen', False):
    # frozen
    dir_ = os.path.dirname(sys.executable)
else:
    # unfrozen
    dir_ = os.path.dirname(os.path.realpath(__file__))

# IMG_PATH = IMG_PATH.append(os.path.join(dir_, 'images'))


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
