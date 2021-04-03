from collections import namedtuple

_VersionInfo = namedtuple("_VersionInfo", "major minor patch")
version_info = _VersionInfo(0, 1, 0)

__version__ = ".".join(version_info)
__license__ = "MIT"
__author__ = "FalseDev"
__title__ = "discord-ext-wizard"
__copyright__ = "Copyright 2021 {}".format(__author__)
__uri__ = "https://github.com/{}/{}".format(__author__, __title__)

from .prompt import Prompt
from .wizard import EmbedWizard, WizardFailure
