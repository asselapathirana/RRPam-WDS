from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA

from rrpam_wds.project_manager import WLCThread

from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main
import rrpam_wds.constants as c


def uniquestring():
    return str(uuid4())


class TC(Test_Parent):

    def test_selection_calculation_of_wlc_returns_correct_results(self):
        from PyQt5.QtCore import pyqtSignal
        from PyQt5.QtCore import QObject

        class PM(QObject):
            def callwithmyid(self, id):
                pass
            heres_a_curve_signal = pyqtSignal(object)
        pm=PM()
        class testData:
            id = "P2"
            requestingcurve="boo"
            years=100
            cons=200000*.32
            r=3
            A=.022
            lunits=c.METERS
            N0=0.081
            length=300
            age=20
            cost=1.0*1.e6*length/1000.
            
        pd=testData()
        wlcthread=WLCThread(pm, pd)
        wlcthread.do_the_job()
        self.assertAlmostEqual(wlcthread.result.damagecost[50],102579,delta=10000)
        self.assertAlmostEqual(wlcthread.result.renewalcost[50],68000,delta=1000)
        
        
 

if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
