import os

from guidata.configtools import add_image_module_path
from guiqwt.config import CONF

import rrpam_wds
import rrpam_wds.constants as c
from rrpam_wds.gui import monkey_patch_guiqwt_guidata

# there are some changes to the guiqwt classes to be done. It is not easy to do this by subclassing, as
# we need to use make.* facotry.
monkey_patch_guiqwt_guidata._patch_all()
# show guiqwt where the images are.
add_image_module_path("rrpam_wds.gui", "images")
# this how we change an option

# if there is not .config directory in the home directory, create it.
configfile = os.path.join(c.HOMEDIR, '.config')
if (os.path.isfile(configfile) and (not os.path.isdir(configfile))):
    os.unlink(configfile)
if (not os.path.isdir(configfile)):
    os.mkdir(configfile)

DEFAULTS = {
    'plot':
    {
        "selection/distance": 10,
    }
}
CONF.update_defaults(DEFAULTS)
CONF.set_application("rrpamwds", version=rrpam_wds.__version__)


def save():
    CONF.save()
