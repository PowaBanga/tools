
__module_name__ = "iZWS"
__module_version__ = "0.1"
__module_description__ = \
    "Inserts a Zero Width Space at the current cursor position.\n" \
    "Configuring a shortcut to use this command is recommended."

import hexchat

def insert_zws(word, word_eol, userdata):

    text = hexchat.get_info('inputbox')
    cursor = hexchat.get_prefs('state_cursor')
    text = text[:cursor] + '\u200B' + text[cursor:]
    hexchat.command('SETTEXT {}'.format(text))
    hexchat.command('SETCURSOR {}'.format(cursor+1))

    return hexchat.EAT_ALL


hexchat.hook_command('ZWS', insert_zws)
