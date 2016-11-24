""" pyton 2.7 by deafult users pyqtv1 api. That runs into conflict with guidata
so, import this file first thing to try to avoid that. """
from PyQt5.QtCore import QObject
import sip

sip.setapi(u'QDate', 2)
sip.setapi(u'QDateTime', 2)
sip.setapi(u'QString', 2)
sip.setapi(u'QTextStream', 2)
sip.setapi(u'QTime', 2)
sip.setapi(u'QUrl', 2)
sip.setapi(u'QVariant', 2)
