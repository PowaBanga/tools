


import hexchat
import re
import random
from collections import namedtuple

UserTuple = namedtuple('UserTuple', 'nick user host')


# wrap around a hexchat context so "prnt" behaves a bit more like print()
# and also add print(), since this works now with python3
class Context:
    def __init__(self, ctx):
        self.ctx = ctx
    
    def __getattr__(self, name):
        return getattr(self.ctx, name)
    
    def prnt(self, *args):
        return self.ctx.prnt(' '.join(str(value) for value in args))
    
    def print(self, *args):
        return self.prnt(*args)
    
    def __repr__(self):
        d = {
            'network': self.ctx.get_info('network'),
            'server': self.ctx.get_info('server'),
            'channel': self.ctx.get_info('channel'),
        }
        return 'Context(network={network!r} server={server!r} '\
            'channel={channel!r})'.format(**d)



# simulate a print event using "Generic Message"
def _emit_print(event_name, *args):
    p = hexchat.get_info('event_text {}'.format(event_name))
    
    # replacing these thingies
    p = p.replace('%C', '\x03')
    p = p.replace('%B', '\x02')
    p = p.replace('%O', '\x0F')
    p = p.replace('%U', '\x1F')
    p = p.replace('%I', '\x1D')
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


# creates a new context with the given name, if it doesn't exist. returns the context.
def get_or_create_context(contextname):
    ctx = hexchat.find_context(server=contextname)
    if ctx is None:
        hexchat.command('newserver -noconnect "{}"'.format(contextname))
        ctx = hexchat.find_context(server=contextname)
    return Context(ctx)


# RFC 1459 - 2.3.1
# <prefix>   ::= <servername> | <nick> [ '!' <user> ] [ '@' <host> ]
def split_prefix(prefix):
    if '!' in prefix:
        nick, _, userhostpart = prefix.partition('!')
        user, _, host = userhostpart.partition('@')
    else:
        nick, _, host = prefix.partition('@')
        user = ''
    return UserTuple(nick, user, host)




# function to request Data from another plugin
def request_data(cmd, callback, params='', timeout=5000, timeoutcb=None):
    s = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # create random command name
    randcmd = ''.join(s[random.randrange(len(s))] for n in range(20))
    
    # local callback functions for the random command names
    def _local(word, word_eol, return_list):
        return_list.append((['*']+word[1:], ['* '+word_eol[1]]+word_eol[1:]))
        return hexchat.EAT_HEXCHAT
    
    def _localend(word, word_eol, ud):
        hexchat.unhook(ud[2]) #hook_id
        hexchat.unhook(ud[3]) #hook_end_id
        hexchat.unhook(ud[4]) #hook_timeout_id
        hexchat.unhook(ud[5]) #hook_421_id
        ud[1](Context(hexchat.get_context()), ud[0])
        return hexchat.EAT_HEXCHAT
    
    def _timeout(ud):
        hexchat.unhook(ud[2])
        hexchat.unhook(ud[3])
        hexchat.unhook(ud[4])
        hexchat.unhook(ud[5])
        if timeoutcb is not None:
            timeoutcb()
    
    def _notfound(word, word_eol, ud):
        if cmd.lower() == word[3].lower():
            # command was sent to server and we received a "not found"
            hexchat.prnt("Could not request data. "\
                "Command {!r} is not a hook.".format(cmd))
            hexchat.unhook(ud[2])
            hexchat.unhook(ud[3])
            hexchat.unhook(ud[4])
            hexchat.unhook(ud[5])
        return hexchat.EAT_NONE
    
    return_list = []
    userdata = []
    
    userdata.append(return_list)
    userdata.append(callback)
    
    hook_id = hexchat.hook_command(
        randcmd, _local, userdata=return_list)
    userdata.append(hook_id)
    
    hook_end_id = hexchat.hook_command(
        randcmd+'END', _localend, userdata=userdata)
    userdata.append(hook_end_id)
    
    hook_421_id = hexchat.hook_server(
        '421', _notfound, userdata=userdata)
    userdata.append(hook_421_id)
    
    if timeout > 0:
        # note: if timeout <= 0, and no hook_timer is set. if an error
        # occurs (esp. if randcmd+'END' never gets sent by the providing
        # plugin), the randcmd hooks might never get unhooked.
        hook_timeout_id = hexchat.hook_timer(
            timeout, _timeout, userdata=userdata)
        userdata.append(hook_timeout_id)
    
    # finally: call the remote command (/testi in this case)
    hexchat.command(("{} {} {}".format(cmd.strip(), randcmd, params)).strip())
    
