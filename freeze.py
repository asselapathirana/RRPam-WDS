import os
import shutil
import sys

import setupdata as sd
from guidata import disthelpers as dh

name = sd.name
version = sd.version
license = sd.license
description = sd.description
author = sd.author
author_email = sd.author_email
url = sd.url


qtlibloc = None
qtlibloc = os.environ.get('QT_QPA_PLATFORM_PLUGIN_PATH', None)
if (not qtlibloc):
    p = os.path.join(sys.exec_prefix, "Library", "plugins", "platforms")
    print("I did not find QT_QPA_PLATFORM_PLUGIN_PATH set. So, trying usual place %s ..." % (p))
    if (os.path.isdir(p)):
        qtlibloc = p
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qtlibloc
        print("Set QT_QPA_PLATFORM_PLUGIN_PATH=%s" % (p))
    else:
        p = os.path.join(sys.exec_prefix, "plugins", "platforms")
        if (os.path.isdir(p)):
            qtlibloc = p
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qtlibloc
            print("Set QT_QPA_PLATFORM_PLUGIN_PATH=%s" % (p))
        else:
            print("I can not find it!")

if (not qtlibloc):
    print(
        " Need to define environmental variable QT_QPA_PLATFORM_PLUGIN_PATH pointing to qt dll files. ")
    raise Exception


binincludes = []
binincludes.extend(["qminimal.dll", "qoffscreen.dll", "qwindows.dll"])

sys.modules["PyQt4"] = None  # block loading PyQt4 to avoid conflicts with PyQt5!
dist = dh.Distribution()
dist.setup(name, version, description, './src/rrpamwds.pyw')
dist.add_modules('PyQt5', 'guidata', 'guiqwt', 'matplotlib')
dist.build_cx_freeze()  # use `build_py2exe` to use py2exe instead
dest = "./dist/"
src_files = os.listdir(qtlibloc)
for file_name in src_files:
    full_file_name = os.path.join(qtlibloc, file_name)
    if (os.path.isfile(full_file_name)):
        shutil.copy(full_file_name, dest)
        print("Copied: %s to ./dist/." % (full_file_name))

with open("./service/rrpamwds_setup.iss_", mode='r') as script:
    text = script.read()
    text = text.format(name=name, version=version, url=url, rootlocation=os.getcwd() + os.sep)
    with open("./service/rrpamwds_setup.iss", mode='w') as sc:
        sc.write(text)
