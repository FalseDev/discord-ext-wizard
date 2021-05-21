from collections import namedtuple

_VersionInfo = namedtuple("_VersionInfo", "major minor patch")
version_info = _VersionInfo(0, 3, 0)

__version__ = ".".join(str(v) for v in version_info)
__license__ = "MIT"
__author__ = "FalseDev"
__title__ = "discord-ext-wizard"
__copyright__ = "Copyright 2021 {}".format(__author__)
__uri__ = "https://github.com/{}/{}".format(__author__, __title__)

from .checks import *
from .mixins import *
from .prompt import *
from .wizard import *
