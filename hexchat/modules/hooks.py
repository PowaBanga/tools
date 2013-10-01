# -*- coding: utf-8 -*-

import hexchat
import traceback
import tools


CONT_TIMER = 1
STOP_TIMER = 0


_use_error_context = False
_err_context_name = 'Plugin Errors'

def use_error_context(val, context_name=None):
    global _use_error_context, _err_context_name
    if context_name is not None:
        _err_context_name = context_name
    _use_error_context = bool(val)

def get_error_context():
    global _use_error_context, _err_context_name
    if not _use_error_context:
        return hexchat.get_context()
    ctx = hexchat.find_context(server=_err_context_name)
    if ctx is None:
        hexchat.command('newserver -noconnect "{}"'.format(_err_context_name))
        ctx = hexchat.find_context(server=_err_context_name)
    return ctx



class Wrapper():
    
    def __init__(self, func, on_error):
        self.func = func
        if on_error is not None:
            self.on_error = on_error
        else:
            self.on_error = hexchat.EAT_NONE
    
    def set_hook(self, hookid):
        self.hook = hookid
    
    # this is being called on each callback
    def __call__(self, *args, **kwargs):
        try:
            ctx = tools.Context(hexchat.get_context())
            return self.func(ctx, *args, **kwargs)
        except:
            tb = traceback.format_exc()
            if callable(self.on_error):
                try:
                    retval = self.on_error(*args, **kwargs)
                except:
                    tb = traceback.format_exc()
            else:
                retval = self.on_error
            
            errctx = get_error_context()
            errctx.prnt(tb)
            return retval

# decorator for prefixed channel commands (e.g. "!slap")
class ChannelCommand(Wrapper):
    def set_command(self, command):
        self.command = command
    def set_command_prefix(self, prefix):
        self.prefix = prefix
    
    def __call__(self, word, word_eol, userdata):
        # word: [nick, text, modus, identifier]
        text_words = word[1].split()
        if len(text_words) > 0:
            text_word = text_words[0]
            if text_word.lower() == self.prefix.lower() + self.command.lower():
                word[0] = hexchat.strip(word[0]) # nick might be coloured
                if len(word) < 4:
                    word += [None]*(4-len(word))
                word.append(userdata)
                return super(ChannelCommand, self).__call__(*word)
        else:
            return hexchat.EAT_NONE
    

class RemotePlugin(Wrapper):
    
    def send(self, line):
        hexchat.command('{} {}'.format(self._callback_cmd, line))
    
    def _send_end(self):
        hexchat.command('{}END'.format(self._callback_cmd))
    
    def __call__(self, word, word_eol, userdata):
        
        self._callback_cmd = word[1].upper()
        return_value = super(RemotePlugin, self).__call__(self, word, word_eol, userdata)
        self._send_end()
        return return_value
        
    




# hexchat.hook_command
def command(cmd, userdata=None, priority=hexchat.PRI_NORM, help_text=None, on_error=None):
    def decorator(func):
        wrapper = Wrapper(func, on_error)
        hookid = hexchat.hook_command(cmd.upper(), wrapper, userdata, priority, help_text)
        wrapper.set_hook(hookid)
        return wrapper
    return decorator

# hexchat.hook_print
def prnt(cmd, userdata=None, priority=hexchat.PRI_NORM, on_error=None):
    def decorator(func):
        wrapper = Wrapper(func, on_error)
        hookid = hexchat.hook_print(cmd, wrapper, userdata, priority)
        wrapper.set_hook(hookid)
        return wrapper
    return decorator

# hexchat.hook_print_attrs
def print_attrs(cmd, userdata=None, priority=hexchat.PRI_NORM, on_error=None):
    def decorator(func):
        wrapper = Wrapper(func, on_error)
        hookid = hexchat.hook_print_attrs(cmd, wrapper, userdata, priority)
        wrapper.set_hook(hookid)
        return wrapper
    return decorator


# hexchat.hook_server
def server(cmd, userdata=None, priority=hexchat.PRI_NORM, on_error=None):
    def decorator(func):
        wrapper = Wrapper(func, on_error)
        hookid = hexchat.hook_server(cmd.upper(), wrapper, userdata, priority)
        wrapper.set_hook(hookid)
        return wrapper
    return decorator

# hexchat.hook_server_attrs
def server_attrs(cmd, userdata=None, priority=hexchat.PRI_NORM, on_error=None):
    def decorator(func):
        wrapper = Wrapper(func, on_error)
        hookid = hexchat.hook_server_attrs(cmd.upper(), wrapper, userdata, priority)
        wrapper.set_hook(hookid)
        return wrapper
    return decorator

# hexchat.hook_timer
def timer(timeout, userdata=None, on_error=None):
    def decorator(func):
        wrapper = Wrapper(func, on_error)
        hookid = hexchat.hook_timer(timeout, wrapper, userdata)
        wrapper.set_hook(hookid)
        return wrapper
    return decorator

# hexchat.hook_unload
def unload(timeout, userdata=None, on_error=None):
    def decorator(func):
        wrapper = Wrapper(func, on_error)
        hookid = hexchat.hook_unload(timeout, wrapper, userdata)
        wrapper.set_hook(hookid)
        return wrapper
    return decorator


# channel command, using a command prefix symbol(s)
# e.g. someone writes "!slap foo bar", then "!" is the prefix, "slap" the hooked
# command, and "foo bar" additional parameters.
def chancmd(prefix, cmd, userdata=None, priority=hexchat.PRI_NORM, on_error=None):
    def decorator(func):
        wrapper = ChannelCommand(func, on_error)
        wrapper.set_command(cmd)
        wrapper.set_command_prefix(prefix)
        hookid = hexchat.hook_print('Channel Message', wrapper, userdata, priority)
        wrapper.set_hook(hookid)
        return wrapper
    return decorator

# use example:
# prefixed = prefixer('!')
# @prefixed('slap')
def prefixer(prefix):
    def _chancmd(*args, **kwargs):
        return chancmd(prefix, *args, **kwargs)
    return _chancmd
    


# extra hooks
def provide(cmd, userdata=None, priority=hexchat.PRI_NORM, help_text=None, on_error=None):
    def decorator(func):
        wrapper = RemotePlugin(func, on_error)
        hookid = hexchat.hook_command(cmd, wrapper, userdata, priority, help_text)
        wrapper.set_hook(hookid)
        return wrapper
    return decorator





