import logging.config
import os

import yaml
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication

DEFAULTCONFIG = os.path.join(os.path.dirname(__file__), 'log', 'logging.yml')


class LogSender(QObject):
    logsender_signal = pyqtSignal(object)

    def __init__(self):
        super(LogSender, self).__init__()
        if not hasattr(self, 'logsender_signal'):
            LogSender.logsender_signal = pyqtSignal(object)


class EmittingLogger(logging.Handler):

    def __init__(self):
        super(EmittingLogger, self).__init__()
        # self.widget = QPlainTextEdit(parent)
        # self.widget.setReadOnly(True)
        self.logsender = LogSender()
        self.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    def emit(self, record):
        msg = self.format(record)
        # self.widget.appendPlainText(msg)
        self.logsender.logsender_signal.emit(msg)


def setup_logging(default_path=DEFAULTCONFIG, default_level=logging.INFO,
                  env_key='LOG_CFG'):
    """Setup logging configuration

    """

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    else:
        logging.basicConfig(level=default_level)
    # emittinglogger=EmittingLogger()

    # logger=logging.getLogger()
    # logger.addHandler(emittinglogger)


@pyqtSlot(object)
def reciever(object):
    pass
    # print("I Got: ", str(object))


if __name__ == "__main__":
    from rrpam_wds.gui.dialogs import MainWindow

    app = QApplication([])

    mw = MainWindow()
    # setup_logging()

    # logger=logging.getLogger()
    # win=QPlainTextEdit()
    # mw.mdi.addSubWindow(win)
    # print(logger.handlers)
    # from rrpam_wds.logger import EmittingLogger
    # handler=[x for x in logger.handlers if isinstance(x,EmittingLogger)][0]
    # handler.logsender.logsender_signal.connect(reciever)
    # handler.logsender.logsender_signal.connect(win.appendPlainText)
    logger = logging.getLogger()
    logger.info("Hello, world!")
    logger.info("Hello, world!")
    mw.show()
    mw.show_logwindow()
    mw.show_logwindow()

    mw.show_logwindow()

    app.exec_()
