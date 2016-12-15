import logging
import os
import sys


def set_paths():
    if (getattr(sys, 'frozen', False)):
        logger = logging.getLogger()
        logger.info("I am frozen")
        logger = logging.getLogger()
        logger.info("I need the platform library files in the same directory with me!")
        logger = logging.getLogger()
        logger.info(
            "(on windows there are at Library/plugins/platforms on POSIXes plugin/platforms)")
        p = os.path.dirname(sys.executable)
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = p
        sys.path.append(p)
    else:
        logger = logging.getLogger()
        logger.info("I am not frozen!")
        logger = logging.getLogger()
        logger.info(
            "If you get platform plugin not found error you may have to point QT_QPA_PLATFORM_PLUGIN_PATH to platforms directory ")
        logger = logging.getLogger()
        logger.info(
            "(on windows there are at Library/plugins/platforms on POSIXes plugin/platforms)")


set_paths()
