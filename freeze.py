import sys
import os

binincludes=[]
binincludes.extend(["qminimal.dll","qoffscreen.dll","qwindows.dll"])

sys.modules["PyQt4"]=None
from guidata import disthelpers as dh
dist = dh.Distribution()
dist.setup('example', '1.0', 'guiqwt app example', './src/run.py')
dist.add_modules('PyQt5','guidata', 'guiqwt')

dist.build_cx_freeze()  # use `build_py2exe` to use py2exe instead
