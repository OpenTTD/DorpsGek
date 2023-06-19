import inspect

from supybot import callbacks, irclib

COMMAND_WHITELIST = {
    "Services": (
        "ghost",
        "identify",
        "op",
    ),
    "Math": (
        "base",
        "calc",
        "convert",
        "icalc",
        "rpn",
        "units",
    ),
    "OpenTTD": ("ports",),
    "Owner": (),
    "SimpleUser": (
        "hostmask",
        "whoami",
    ),
    "Topic": (
        "add",
        "change",
        "get",
        "remove",
        "replace",
        "set",
        "topic",
    ),
    "WebLogsS3": ("logs",),
    "Channel": (
        "dehalfop",
        "deop",
        "devoice",
        "halfop",
        "kban",
        "kick",
        "limit",
        "mode",
        "moderate",
        "op",
        "unban",
        "unmoderate",
        "voice",
    ),
}


# Hook into "addCallback" of Irc, which is the point a plugin registers itself
# to the system. It is also called on reloads, etc.
def patched_addCallback(self, callback):
    # Disable all commands accept for the whitelist. This is because by default
    # these plugins allow a bunch of commands you really do not want it to allow.
    # Some are very spammy, others are a security risk, others just make no sense
    # to have in this plugin, etc. So, instead, we whitelist what is allowed.
    for name in dir(callback):
        item = getattr(callback, name)

        if hasattr(item, "__code__"):
            code = item.__code__
            if inspect.getargs(code)[0] == ["self", "irc", "msg", "args"]:
                if name not in COMMAND_WHITELIST.get(callback.__class__.__name__, ()):
                    setattr(callback, name, None)

        if issubclass(item.__class__, callbacks.Commands):
            setattr(callback, name, None)

    return irclib.original_addCallback(self, callback)


# Ensure we only capture the original function once; this plugin can be
# reloaded many times.
if not hasattr(irclib, "original_addCallback"):
    irclib.original_addCallback = irclib.Irc.addCallback
irclib.Irc.addCallback = patched_addCallback


class Aaa_HideCommands(callbacks.Plugin):
    """Hide commands that are not on the whitelist for other plugins."""


Class = Aaa_HideCommands
