from rrpam_wds.gui import set_pyqt_api   # isort:skip # NOQA

import logging
import sys

from PyQt5.QtWidgets import QApplication

import rrpam_wds.gui.dialogs


class ProjectGUI():
    logger = logging.getLogger()

    def new_project(self):
        self.logger.info("New Project")

    def open_project(self):
        self.logger.info("Open Project")

    def save_project(self):
        self.logger.info("Save Project")

    def close_project(self):
        self.logger.info("Close Project")


def main():
    app = QApplication(sys.argv)
    ex = rrpam_wds.gui.dialogs.MainWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
