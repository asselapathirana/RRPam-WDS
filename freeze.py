import os
import glob
import shutil
import sys
import setupdata as sd
from guidata import disthelpers as dh
import email

dest = "./dist/"



name = sd.name
version = sd.version
license = sd.license
description = sd.description
author = sd.author
author_email = sd.author_email
url = sd.url

start_file='./src/rrpamwds.pyw'

if (len(sys.argv) > 1 and str.lower(sys.argv[1])== "debug"):
    start_file='./src/rrpamwds.py'
    
print ("tragetting start file %s" % (start_file))


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



sys.modules["PyQt4"] = None  # block loading PyQt4 to avoid conflicts with PyQt5!
dist = dh.Distribution()
dist.setup(name, version, description, start_file, includes=[ ])
dist.add_modules('PyQt5', 'guidata', 'guiqwt', 'matplotlib')
dist.build_cx_freeze()  # use `build_py2exe` to use py2exe instead

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

def copy_necessary_files(sys, os, glob, dest, shutil):
    # copy the needed dll files and libraries that cx_free misses

    l=os.path.dirname(sys.executable)
    loc=os.path.join(l,"Library","bin")
    if (os.path.isdir(loc)):
        for file in glob.glob(os.path.join(loc,"mkl*.dll")):
            print ("Copying mkl library  %s" %(file))
            shutil.copy(file,dest)
        for file in glob.glob(os.path.join(loc,"libiomp5md.dll")):
            print ("Copying library  %s" %(file))
            shutil.copy(file,dest)    

    loc=os.path.join(l,"Lib","email")
    dst=os.path.join(dest,"email")
    if ((not os.path.isdir(dst) ) and os.path.isdir(loc)):
        print ("Copying %s" % (loc))
        shutil.copytree(loc,dst)
        
    loc=os.path.join(l,"Lib","uu.py")
    if (os.path.isfile(loc)):
        print ("Copying %s" % (loc))
        shutil.copy(loc,dest) 
        
copy_necessary_files(sys, os, glob, dest, shutil)
        




