import supybot.conf as conf


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    conf.registerPlugin("WebLogsS3", True)


WebLogsS3 = conf.registerPlugin("WebLogsS3")
