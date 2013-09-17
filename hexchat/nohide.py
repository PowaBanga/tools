# -*- coding: utf-8 -*-

# Python 3.3
# HexChat 2.9.6

__module_name__ = "NoHide Script"
__module_version__ = "1.0"
__module_description__ = "Does *not* hide Part/Leave Message of users that have interacted with the channel."

import hexchat

hexchat.emit_print("Generic Message", "Loading", "{} {} - {}".format(\
    __module_name__, __module_version__, __module_description__))

import time
import os
import re
from collections import defaultdict


nickdict = {}
NICK_TIMEOUT = 60*30 # 30 minutes



# simulate a print event using "Generic Message"
def _emit_print(event_name, *args):
    p = hexchat.get_info('event_text {}'.format(event_name))
    
    # replacing these thingies
    p = p.replace('%C', '\x03')
    p = p.replace('%B', '\x02')
    p = p.replace('%O', '\x0F')
    p = p.replace('%U', '\x1F')
    p = re.sub(r'\$(\d+)', r'{\1}', p) # $1 => {1}
    
    # event_text starts with $1, str.format with {0} so add an empty 
    # {0} element at the beginning
    args = [''] + list(args)
    
    # raises an error if "{N}" refers to an index
    # out of range of "args' (N >= len(word) + 1 + 10)
    try:
        args += ['']*10 # welp
        p = p.format(*args)
    except IndexError:
        p += ' \x0F\x02\x034(IndexError)\x0F'
    
    if '$t' in p:
        leftp, rightp = p.split('$t', 1)
        hexchat.emit_print("Generic Message", leftp, rightp)



def leftjoin(word, word_eol, userdata):
    
    ctx = hexchat.get_context()
    channel = ctx.get_info('channel')
    
    # we need the channel object to get the flags
    chanobj = None
    for chan in hexchat.get_list('channels'):
        if hexchat.nickcmp(chan.channel, channel) == 0:
            chanobj = chan
            break
    
    if chanobj is None:
        return hexchat.EAT_NONE
    
    # if is this isn't a channel with the "Hide Join/Left" option, just return.
    if chanobj.flags & 0x40 == 0:
        return hexchat.EAT_NONE
    
    cleanup(userdata['nicks'])
    
    lnick = hexchat.strip(word[0])
    channel = chan.channel
    
    for dnick, dchannel in userdata['nicks']:
        if hexchat.nickcmp(lnick, dnick) == 0 \
                and hexchat.nickcmp(dchannel, channel) == 0:
            if time.time() <= userdata['nicks'][(dnick, dchannel)]:
                _emit_print(userdata['type'], *word)
                return hexchat.EAT_ALL
            else:
                del userdata['nicks'][(dnick, dchannel)]
    
    return hexchat.EAT_NONE

# analyze the text I send, and look for known nicknames.
def metalk(word, word_eol, userdata):
    global NICK_TIMEOUT
    
    cleanup(userdata)
    text = word[1]
    ctx = hexchat.get_context()
    channel = ctx.get_info('channel').lower()
    
    for user in ctx.get_list('users'):
        if user.nick.lower() in text.lower():
            userdata[(user.nick.lower(), channel)] = time.time() + NICK_TIMEOUT
    return hexchat.EAT_NONE

# when someone posted a message
def textmessage(word, word_eol, userdata):
    global NICK_TIMEOUT
    
    ctx = hexchat.get_context()
    channel = ctx.get_info('channel').lower()
    
    # we need the channel object to get the flags
    chanobj = None
    for chan in hexchat.get_list('channels'):
        if hexchat.nickcmp(chan.channel, channel) == 0:
            chanobj = chan
            break
    
    if chanobj.flags & 0x40 == 0:
        return hexchat.EAT_NONE
    
    nick = hexchat.strip(word[0])
    userdata[(nick, channel)] = time.time() + NICK_TIMEOUT
    return hexchat.EAT_NONE

# be sure to update the dictionary, if the user changes it's nickname.
def nickchange(word, word_eol, userdata):
    oldnick = hexchat.strip(word[0])
    newnick = hexchat.strip(word[1])
    for oldnick, channel in list(userdata.items()):
        if hexchat.nickcmp(oldnick, newnick) == 0:
            userdata[(newnick, channel)] = userdata[(oldnick, channel)]
            del userdata[(oldnick, channel)]
    return hexchat.EAT_NONE


# /nohide command. just displays the current stored nicks per channel.
def nohide(word, word_eol, userdata):
    cleanup(userdata)
    
    if len(word) > 1:
        channel_list = word[1:]
    else:
        channel_list = None
    
    def in_channel_list(chan):
        if channel_list is None:
            return True
        else:
            for c in channel_list:
                if hexchat.nickcmp(c, chan) == 0:
                    return True
            return False
    
    nclist = list(userdata.keys())
    
    chans = defaultdict(list)
    for n, c in nclist:
        chans[c].append(n)
    
    chanlist = list(chans.keys())
    chanlist.sort()
    
    hexchat.emit_print('Generic Message', 'NoHide', \
        '{} Users in {} Channels'.format(len(nclist), len(chanlist)))
    
    for chan in chanlist:
        if in_channel_list(chan):
            nicklist = chans[chan]
            nicklist.sort()
            #hexchat.emit_print('Generic Message', '*', '\x02{}\x02'.format(chan))
            leftpart = '\x02{}\x02'.format(chan)
            hexchat.emit_print('Generic Message', leftpart, '({}) '.format(len(nicklist)) + (', '.join(nicklist)))
        
    return hexchat.EAT_XCHAT


# remove all the nicknames that have timeout
def cleanup(nickdict):
    for nc in list(nickdict.keys()):
        if time.time() > nickdict[nc]:
            del nickdict[nc]
    




for hook in ['Part', 'Part with Reason', 'Join', 'Quit']:
    hexchat.hook_print(hook, leftjoin, \
        userdata={'nicks': nickdict, 'type': hook})

for hook in ['Channel Action Hilight', 'Channel Msg Hilight', \
        'Channel Message', 'Channel Action']:
    hexchat.hook_print(hook, textmessage, userdata=nickdict)

hexchat.hook_print('Your Message', metalk, userdata=nickdict)
hexchat.hook_print('Your Action', metalk, userdata=nickdict)
hexchat.hook_print('Change Nick', nickchange, userdata=nickdict)

hexchat.hook_command('NOHIDE', nohide, userdata=nickdict)

#hexchat.hook_print('Kick', log_part)
#hexchat.hook_print('Join', log_join)

