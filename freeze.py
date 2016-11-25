import sys
import os
import shutil
from setupdata import *

qtlibloc=os.environ['QT_QPA_PLATFORM_PLUGIN_PATH']
if (not qtlibloc):
    p=os.path.join(sys.exec_prefix,"Library""plugins""platforms")
    print("I did not find QT_QPA_PLATFORM_PLUGIN_PATH set. So, trying usual place ...")
    if (os.direxists(p)):
        qtlibloc=p
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH']=qtlibloc
        print ("Set QT_QPA_PLATFORM_PLUGIN_PATH=%s" %(p))
        
if (not qtlibloc):
    print (" Need to define environmental variable QT_QPA_PLATFORM_PLUGIN_PATH pointing to qt dll files. ")
    raise Exception

name='rrpam-wds'
version='0.1.0'
license='GPLV3'
description='Risk-based renewal planning for asset management of water distribution systems'
author='Assela Pathirana'
author_email='assela@pathirana.net'
url='https://github.com/asselapathirana/RRPam-WDS'


binincludes=[]
binincludes.extend(["qminimal.dll","qoffscreen.dll","qwindows.dll"])

sys.modules["PyQt4"]=None # block loading PyQt4 to avoid conflicts with PyQt5!
from guidata import disthelpers as dh
dist = dh.Distribution()
dist.setup(name,version,description, './src/rrpamwds.pyw')
dist.add_modules('PyQt5','guidata', 'guiqwt')
dist.build_cx_freeze()  # use `build_py2exe` to use py2exe instead
dest="./dist/"
src_files = os.listdir(qtlibloc)
for file_name in src_files:
    full_file_name = os.path.join(qtlibloc, file_name)
    if (os.path.isfile(full_file_name)):
        shutil.copy(full_file_name, dest)
        print ("Copied: %s to ./dist/." % (full_file_name))
        
with open("./service/rrpamwds_setup.iss_", mode='r') as script:
    text=script.read()
    text=text.format(name=name,version=version,url=url,rootlocation=os.getcwd()+os.sep)
    with open("./service/rrpamwds_setup.iss",mode='w') as sc:
        sc.write(text)