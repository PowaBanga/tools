# -*- coding: utf-8 -*-

# Python 3.3
# HexChat 2.9.6

__module_name__ = "ZNC Buffextras"
__module_version__ = "1.0"
__module_description__ = "Displays the *buffextra lines from ZNC Buffextra " \
    "module nicely. Python implementation."

import hexchat
hexchat.emit_print("Generic Message", "Loading", "{} {} - {}".format(
                   __module_name__, __module_version__,
                   __module_description__))
import time


def privmsg(word, word_eol, userdata, attributes):

    bprefix = word[0]
    if bprefix[0:1] != ':':
        return hexchat.EAT_NONE

    bprefix = bprefix[1:]
    bnick, _, bhost = split_prefix(bprefix)

    if bnick == '*buffextras':

        if attributes.time:
            bufftime = attributes.time
        else:
            bufftime = int(time.time())

        channel = word[2]
        prefix = word[3][1:]
        _type = word[4]
        args = word_eol[5] if word[5:] else ''

        nick, user, host = split_prefix(prefix)

        if _type == 'set':
            hexchat.emit_print(
                "Channel Modes", channel, args[6:],
                time=bufftime)
        elif _type == 'joined':
            hexchat.emit_print(
                "Join", nick, channel, host,
                time=bufftime)
        elif _type == 'parted':
            if args.startswith('with message: ['):
                hexchat.emit_print(
                    "Part with Reason", nick, host, channel, args[15:-1],
                    time=bufftime)
            else:
                hexchat.emit_print(
                    "Part", nick, host, channel,
                    time=bufftime)
        elif _type == 'is':
            hexchat.emit_print(
                "Change Nick", nick, args[13:],
                time=bufftime)
        elif _type == 'quit':
            hexchat.emit_print(
                "Quit", nick, args[15:-1], host,
                time=bufftime)
        elif _type == 'kicked':
            hexchat.emit_print(
                "Kick", nick, word[5],
                channel, word_eol[6][9:-1],
                time=bufftime)
        elif _type == 'changed':
            hexchat.emit_print(
                "Topic Change", nick,
                args[14:], channel,
                time=bufftime)
        else:
            hexchat.emit_print(
                "Server Error",
                "Unhandled *buffextras event:",
                time=bufftime)
            hexchat.emit_print(
                "Server Error",
                "    {}".format(word_eol[3][1:]),
                time=bufftime)
        return hexchat.EAT_HEXCHAT

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
