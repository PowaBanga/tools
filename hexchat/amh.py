#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python 3.3
# HexChat 2.9.6

__module_name__ = "Anti Massive Highlight"
__module_version__ = "1.0"
__module_description__ = "Hides messages that contain lots of nicknames."

import hexchat
hexchat.emit_print("Generic Message", "Loading", "{} {} - {}".format(
                   __module_name__, __module_version__,
                   __module_description__))


def privmsg(word, word_eol, userdata, attrs):
    ctx = hexchat.get_context()
    users = ctx.get_list('users')
    nicks = {user.nick.lower() for user in users}
    words = {w.lower() for w in word_eol[3][1:].split()}
    if len(nicks & words) >= 5:
        return hexchat.EAT_ALL
    return hexchat.EAT_NONE


# extra tools
def split_prefix(prefix):

    if '!' in prefix:
        nick, _, userhostpart = prefix.partition('!')
        user, _, host = userhostpart.partition('@')
    else:
        nick, _, host = prefix.partition('@')
        user = ''

    return (nick, user, host)


hexchat.hook_server_attrs('PRIVMSG', privmsg)
