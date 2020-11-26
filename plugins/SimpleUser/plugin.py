import supybot.ircdb as ircdb
from supybot.commands import wrap, additional
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization("SimpleUser")


class SimpleUser(callbacks.Plugin):
    """A very simple user authentication. As in, it fully depends on
    hostmask."""

    @internationalizeDocstring
    def hostmask(self, irc, msg, args, nick):
        """[<nick>]

        Returns the hostmask of <nick>.  If <nick> isn't given, return the
        hostmask of the person giving the command.
        """
        if not nick:
            nick = msg.nick
        irc.reply(irc.state.nickToHostmask(nick))

    hostmask = wrap(hostmask, [additional("seenNick")])

    @internationalizeDocstring
    def whoami(self, irc, msg, args):
        """takes no arguments

        Returns the name of the user calling the command.
        """
        try:
            user = ircdb.users.getUser(msg.prefix)
            irc.reply(user.name)
        except KeyError:
            error = _("I don't recognize you.")
            irc.reply(error)

    whoami = wrap(whoami)


Class = SimpleUser
