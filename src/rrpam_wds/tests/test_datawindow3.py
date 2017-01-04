from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import os
import time

import mock

import rrpam_wds.constants as c
from rrpam_wds.examples import networks
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main


class TC(Test_Parent):
    logger = logging.getLogger()

    def get_ids(self):
        l = self.aw.datawindow.get_information()[1]
        return [self.aw.datawindow._getgroupname(x[0]) for
                x in enumerate(l)]

    def get_choices(self, QComboBoxName):
        return [QComboBoxName.itemText(i) for i in range(QComboBoxName.count())]

    def test_each_assign_asset_item_has_diameter_length_and_id(self):
        self.create_a_new_project()
        for id_, item in self.aw.datawindow.myplotitems.items():
            self.assertEqual(id_, item.id_)
            self.assertEqual(item.my_id.text(), item.id_)
            self.assertEqual(item.my_dia.text(), str(item.diameter_))
            self.assertEqual(item.my_length.text(), str(item.length_))
            
    def test_select_diameter_combobox_has_unique_diameters(self):
        self.create_a_new_project()
        combo=self.aw.datawindow.ui.select_diameter_combobox
        AllItems = set(combo.itemText(i) for i in range(combo.count()))
        self.assertSetEqual(AllItems,set([u'8.0', u'14.0', u'10.0', u'0.0', u'12.0', u'6.0', u'18.0']))
        
    def test_pressing_select_diameter_button_will_select_items_with_current_diameter(self):
        self.create_a_new_project()
        from PyQt5.QtTest import QTest
        from PyQt5.QtCore import Qt         
        self.aw.datawindow.ui.select_diameter_combobox.setCurrentIndex(3)  
        self.assertEqual(self.aw.datawindow.ui.select_diameter_combobox.currentText(),'10.0')
        QTest.mouseClick(self.aw.datawindow.ui.select_diameter_button, Qt.LeftButton)
        sel2 = [x.id_ for x in self.aw.networkmap.get_plot().get_selected_items() if (hasattr(x, "id_"))]
        sel  = [x.id_ for x in self.aw.datawindow.get_plot().get_selected_items() if (hasattr(x, "id_"))]
        self.assertSetEqual(set(sel),set(['12','21', '111']))
        self.assertSetEqual(set(sel),set(sel2))
        self.aw.datawindow.ui.select_diameter_combobox.setCurrentIndex(2)       
        self.assertEqual(self.aw.datawindow.ui.select_diameter_combobox.currentText(),'8.0')
        
        QTest.mouseClick(self.aw.datawindow.ui.select_diameter_button, Qt.LeftButton)
        sel2 = [x.id_ for x in self.aw.networkmap.get_plot().get_selected_items() if (hasattr(x, "id_"))]
        sel  = [x.id_ for x in self.aw.datawindow.get_plot().get_selected_items() if (hasattr(x, "id_"))]        
        self.assertSetEqual(set(sel),set(['113','121']))
      
    def test_pressing_copytoselection_button_will_make_selected_assets_have_current_group(self):
        self.create_a_new_project()
        from PyQt5.QtTest import QTest
        from PyQt5.QtCore import Qt   
        self.test_pressing_select_diameter_button_will_select_items_with_current_diameter() # now we have 113 and 121 selected
        dw=self.aw.datawindow
        dw.ui.no_groups.setValue(4)
        dw.ui.grouptocopy.setCurrentText(dw._getgroupname(1)) # we have selected group G01
        self.assertEqual(dw.myplotitems['113'].my_group.currentText(),
                         dw._getgroupname(0)) # still the group of this item should be G00
        #now click the button
        QTest.mouseClick(dw.ui.copytoselection, Qt.LeftButton)
        self.assertEqual(dw.myplotitems['113'].my_group.currentText(),
                                 dw._getgroupname(1)) # still the group of this item should be G00        
        self.assertEqual(dw.myplotitems['121'].my_group.currentText(),
                                 dw._getgroupname(1)) # still the group of this item should be G00        

        
        
    def create_a_new_project(self):
        import tempfile
        with mock.patch.object(self.aw.projectgui, '_getSaveFileName', autospec=True) as mock__getSaveFileName:
            with mock.patch.object(self.aw.projectgui, '_getSaveFileName2', autospec=True) as mock__getSaveFileName2:
                sf = os.path.join(tempfile.tempdir, "xxx3xp")
                mock__getSaveFileName.return_value = (sf, c.PROJECTEXTENSION)
                mock__getSaveFileName2.return_value = (networks[0], '*.inp')
                self.aw._new_project()
                time.sleep(.1)
                self.app.processEvents()

                # make sure the thread finishes
                self.aw.pm.wait_to_finish()
                self.app.processEvents()
                time.sleep(.1)
                return sf


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
