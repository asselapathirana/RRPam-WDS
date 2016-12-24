from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import unittest
from uuid import uuid4

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QDialog
import shutil
import rrpam_wds.constants as c

from rrpam_wds.tests.test_utils import Test_Parent, set_text_spinbox, set_text_textbox
from rrpam_wds.tests.test_utils import main
import logging
import mock
import tempfile
import os


class TC(Test_Parent):
    logger=logging.getLogger()
    
    

if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
