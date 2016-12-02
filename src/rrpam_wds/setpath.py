import sys
import os

def set_paths():
    if (getattr(sys, 'frozen', False)):
        print("I am frozen")
        print("I need the platform library files in the same directory with me!")
        print("(on windows there are at Library/plugins/platforms on POSIXes plugin/platforms)")
        p = os.path.dirname(sys.executable)
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = p
        sys.path.append(p)
    else:
        print("I am not frozen!")
        print(
            "If you get platform plugin not found error you may have to point QT_QPA_PLATFORM_PLUGIN_PATH to platforms directory ")
        print("(on windows there are at Library/plugins/platforms on POSIXes plugin/platforms)")


set_paths()