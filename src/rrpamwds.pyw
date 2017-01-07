import rrpamwds 
from rrpam_wds import __version__ as version
import sys

if sys.platform == "win32":
    import ctypes
    myappid = 'asselapathirana.rrpamwds.%s'%version # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

if __name__=="__main__":
    rrpamwds.main()
