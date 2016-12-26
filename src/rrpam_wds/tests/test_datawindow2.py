from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging

from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):
    logger = logging.getLogger()
    
    def get_ids(self):
        l=self.aw.datawindow.get_information()[1]
        return [self.aw.datawindow._getgroupname(x[0]) for 
                x in enumerate(l)]
    def get_choices(self, QComboBoxName):
        return [QComboBoxName.itemText(i) for i in range(QComboBoxName.count())]
    def test_group_choices_are_correctly_updated(self):
        choice=self.aw.datawindow.ui.grouptocopy
        # Check doing nothing first
        ids=self.get_ids()
        vals=self.get_choices(choice)
        self.assertEqual(ids,vals)
        


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
