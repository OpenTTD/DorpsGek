"""
Provides a plugin specific for OpenTTD channels.
"""

import supybot

# Use this for the version of this plugin.  You may wish to put a CVS keyword
# in here if you\'re keeping the plugin in CVS or some similar system.
__version__ = "%%VERSION%%"

__author__ = supybot.Author("Patric Stout", "TrueBrain", "truebrain@openttd.org")
__maintainer__ = supybot.Author("Patric Stout", "TrueBrain", "truebrain@openttd.org")

# This is a dictionary mapping supybot.Author instances to lists of
# contributions.
__contributors__ = {}

from . import config
from . import plugin
from importlib import reload

reload(plugin)  # In case we're being reloaded.

Class = plugin.Class
configure = config.configure
