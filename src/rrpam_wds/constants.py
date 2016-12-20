import os
import unicodedata

import appdirs

units = {"EURO": u"{}".format(unicodedata.lookup("EURO SIGN")), "DOLLARS": "$"}
curve_colors = ["b", "r", "p", "g"]
_appdir = appdirs.user_data_dir("RRPAMWDS", "ASSELAPAT")
PROJECTDATA = os.path.join(_appdir, "rrpamwds.dat")
USERDATA = appdirs.user_data_dir(None, None)
PROJECTEXTENSION = ".rrp"
HOMEDIR = os.path.expanduser("~")
PROJECTDATADIREXT = ".datadir"

class ResultSet: pass
