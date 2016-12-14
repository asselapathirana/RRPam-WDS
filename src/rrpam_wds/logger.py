import os
import logging.config

import yaml
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QApplication

DEFAULTCONFIG=os.path.join(os.path.dirname(__file__),'log','logging.yml')

class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super(QPlainTextEditLogger, self).__init__()

        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self, m):
        pass



def setup_logging(default_path=DEFAULTCONFIG,default_level=logging.INFO,
                  env_key='LOG_CFG', parent=None):
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
    if(parent):
        log_handler = QPlainTextEditLogger(parent)
        logging.getLogger().addHandler(log_handler) 
        return log_handler.widget    
    return None



if __name__== "__main__":
    from rrpam_wds.gui.dialogs import MainWindow
    app=QApplication([])
    mw=MainWindow()
    win=setup_logging(parent=mw)
    if(win):
        mw.mdi.addSubWindow(win)
    win.show()
    logger=logging.getLogger(__name__)
    logger.info("Hello, world!")
    mw.show()
    app.exec_()
    
    