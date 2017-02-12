import logging
import os
import unicodedata

import appdirs
import numpy as np

units = {"EURO": u"{}".format(unicodedata.lookup("EURO SIGN")),
         "DOLLARS": "$",
         'LPS': ['m', 'mm'],
         'LPM': ['m', 'mm'],
         'MLD': ['m', 'mm'],
         'CMH': ['m', 'mm'],
         'CMD': ['m', 'mm'],
         # now imperial units
         'CFS': ['ft', 'in'],
         'GPM': ['ft', 'in'],
         'MGD': ['ft', 'in'],
         'IMGD': ['ft', 'in'],
         'AFD': ['ft', 'in'],
         }
curve_colors = ["b", "r", "p", "g"]
widget_select_background = 19
widget_default_background = 10  # see http://doc.qt.io/qt-4.8/qpalette.html#ColorRole-enum
_appdir = appdirs.user_data_dir("RRPAMWDS", "ASSELAPAT")
# PROJECTDATA = os.path.join(_appdir, "rrpamwds.dat")
# USERDATA = appdirs.user_data_dir(None, None)
PROJECTEXTENSION = ".rrp"
HOMEDIR = os.path.expanduser("~")
PROJECTDATADIREXT = ".datadir"

DEFAULT_A = .2238
DEFAULT_N0 = 4.92E-04
DEFAULT_age = 20
DEFAULT_cost = 500.

DIRECTCOSTMULTIPLIER = 1000

METERS = 'm'
FEET = 'ft'
KM = 'km'
MM = 'mm'
MILES = 'mi'
INCHES = 'in'

LENGTH_CONVERSION_FACTOR = {METERS: 1000.0, FEET: 5280.0}

DOCROOT = "docs_"


def _getProb(A, time_, lunits, N, length, age):
    return length / LENGTH_CONVERSION_FACTOR[lunits] * N * np.exp(A * (age + time_))


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class ResultSet:
    pass


class WLCData:
    requestingcurve = None
    id = None
    age = DEFAULT_age
    A = DEFAULT_A
    N0 = DEFAULT_N0
    r = 5.0
    years = 20.
    cost = DEFAULT_cost
    length = 100.
    lunits = METERS
    cons = -999.


class WLCCurve:
    requestingcurve = None
    id = None
    wlccurveindex = 0
    year = []
    damagecost = []
    renewalcost = []
    id_ = None


def _get_dir_and_extention(projectname):
    logger = logging.getLogger()
    logger.info("Analysing prjname : %s", projectname)
    if(projectname[-4:] != PROJECTEXTENSION):
        t = projectname + PROJECTEXTENSION
    else:
        t = projectname
    prjname, subdir, ext = (t, t[:-4] + PROJECTDATADIREXT, t[-4:])
    logger.info("Returning prjname:%s, subdir:%s and ext:%s" % (prjname, subdir, ext))

    return prjname, subdir, ext
