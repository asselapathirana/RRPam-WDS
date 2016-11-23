"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mrrpam_wds` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``rrpam_wds.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``rrpam_wds.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from rrpam_wds.gui.dialogs import MainWindow 
import sys

parser = argparse.ArgumentParser(description='Command description.')
parser.add_argument('names', metavar='NAME', nargs=argparse.ZERO_OR_MORE,
                    help="A name of something.")


def main(args=None):
    args = parser.parse_args(args=args)
    print(args.names)
    app=QApplication([])
    win=MainWindow()
    win.show()
    sys.exit(app.exec_())
    
    return 0
