# -*- encoding: utf-8 -*-

__module_name__ = "Regex Hilight"
__module_version__ = "1.0"
__module_description__ = "Highlighting with Regex"

# Python 3.3
# HexChat 2.9.6

import hexchat
import re
import os
import subprocess
import shlex


# info("some text")
#      -> emit_print("Generic Message", __module_name__, "some text")
# info("left text", "some text")
#      -> emit_print("Generic Message", "left text", "some text")

def info(a, b=None, ctx=None):
    if b is None:
        leftstring = __module_name__
        rightstring = a
    else:
        leftstring = a
        rightstring = b
    
    if ctx is None:
        ctx = hexchat
    ctx.emit_print("Generic Message", leftstring, rightstring)



def settings(ctx=None):
    if ctx is None:
        ctx = hexchat
    info("Current Settings:", ctx=ctx)
    if int(hexchat.get_pluginpref("regexhilight_sound")) == 1:
        info("*", "Sound enabled: Yes", ctx=ctx)
    else:
        info("*", "Sound enabled: No", ctx=ctx)

    info("*", "Soundfile: {}".format(hexchat.get_pluginpref("regexhilight_soundfile")), ctx=ctx)
    info("*", "Soundcommand: {}".format(hexchat.get_pluginpref("regexhilight_soundcmd")), ctx=ctx)



def privmsg(word, word_eol, userdata):
    
    tmp = hexchat.get_prefs("irc_extra_hilight").strip()
    if tmp != userdata['regex_str']:
        userdata['regex_str'] = tmp
        userdata['regex'] = re.compile(userdata['regex_str'], re.I)
    
    mynick = hexchat.get_info('nick')
    nick_regex = re.compile((r'\b{}\b').format(re.escape(mynick)), re.I)
    
    rawtext = word_eol[3][1:]
    text = hexchat.strip(rawtext)
    
    is_action = False
    if rawtext.startswith('\x01ACTION') and rawtext.endswith('\x01'):
        is_action = True
        rawtext = rawtext[7:-1].strip()
    
    nickname = word[0][1:].partition('!')[0].partition('@')[0]
    channel = word[2]
    
    m = userdata['regex'].search(text)
    m2 = nick_regex.search(text)
    if m is not None or m2 is not None:
        
        
        
        soundstate = int(hexchat.get_pluginpref("regexhilight_sound"))
        soundfile = hexchat.get_pluginpref("regexhilight_soundfile")
        soundcmd = hexchat.get_pluginpref("regexhilight_soundcmd")
        if soundstate == 1:
            if soundfile is None or soundcmd is None:
                info("Oops! soundfile or soundcmd is not set. Refer to /help hilight")
            else:
                configdir = hexchat.get_info('configdir')
                soundfile = os.path.join(os.path.expanduser(configdir), 'sounds', soundfile)
                cmd = shlex.split(soundcmd)
                soundfile_set = False
                for i,c in enumerate(cmd):
                    if '{file}' in c:
                        cmd[i] = c.format(**{'file': soundfile})
                        soundfile_set = True
                if not soundfile_set:
                    cmd.append(soundfile)
                ret = subprocess.Popen(cmd)
        
        
        #channel = hexchat.get_info('channel')
        network = hexchat.get_info('network')
        ctx = hexchat.get_context()
        
        
        for chan in ctx.get_list('channels'):
            if chan.channel == channel and chan.network == network:
                oldctx = ctx
                chan.context.set() #dunno if this is necessary
                hexchat.command("gui color 3")
                hexchat.command("gui flash")
                if is_action:
                    chan.context.emit_print("Channel Action Hilight", nickname, rawtext, '')
                else:
                    chan.context.emit_print("Channel Msg Hilight", nickname, rawtext, '')
                oldctx.set()
                return hexchat.EAT_XCHAT
    
    return hexchat.EAT_NONE

def hilight(word, word_eol, userdata):
    if len(word) <= 1:
        info("Not enough parameters. Refer to /HELP HILIGHT")
        return hexchat.EAT_ALL
    
    cmd = word[1].upper()
    
    if cmd == 'SET':
        if len(word) <= 2:
            info("Not enough parameters. Refer to /HELP HILIGHT")
            return hexchat.EAT_ALL
        
        subcmd = word[2].upper()
        
        if subcmd == 'FILE':
            hexchat.set_pluginpref("regexhilight_soundfile", word_eol[3])
            info("Set soundfile to: {}".format(word_eol[3]))
        elif subcmd == 'COMMAND':
            hexchat.set_pluginpref("regexhilight_soundcmd", word_eol[3])
            info("Command set to: {}".format(word_eol[3]))
        elif subcmd == 'ON':
            hexchat.set_pluginpref("regexhilight_sound", 1)
            info("Sound hilight enabled")
        elif subcmd == 'OFF':
            hexchat.set_pluginpref("regexhilight_sound", 0)
            info("Sound hilight disabled")
        else:
            info("Unknown command: SET {}".format(subcmd))
    elif cmd == 'INFO':
        print('info..')
        settings(hexchat)
    else:
        info("Unknown command.")
    hexchat.EAT_ALL




ud = {}
ud['regex_str'] = hexchat.get_prefs("irc_extra_hilight").strip()
ud['regex'] = re.compile(ud['regex_str'], re.I)


help_text = '''
Usage: /HILIGHT INFO
Usage: /HILIGHT SET ( ON | OFF | FILE <soundfile> | COMMAND <shell-command> )

/HILIGHT INFO
    Displays the current settings.
/HILIGHT SET ( ON | OFF )
    Enables or disables the usage of soundfiles.
/HILIGHT SET FILE <soundfile>
    Is a file located in the "sounds" directory of your hexchat installation.
/HILIGHT SET COMMAND <shell-command>
    Is command that should be used to play the soundfile. May contain {file}
    placeholder, so the script knows where to place the soundfile.
'''

if hexchat.get_pluginpref("regexhilight_sound") is None:
    hexchat.set_pluginpref("regexhilight_sound", 0)

hexchat.hook_server("PRIVMSG", privmsg, userdata=ud)
hexchat.hook_command("HILIGHT", hilight, help=help_text)
hexchat.hook_command("HL", hilight, help=help_text)

hexchat.emit_print("Generic Message", __module_name__, "Loaded!")
