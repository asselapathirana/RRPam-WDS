from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging

from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):
    logger = logging.getLogger()


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
