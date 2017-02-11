
from collections import namedtuple

import hexchat

__module_name__ = "ZNC Auto Complete"
__module_version__ = "0.1"
__module_description__ = "Adds auto complete functionality for ZNC commands."
__module_author__ = "Nitori"


KEY_TAB = 65289
BoxInfo = namedtuple('BoxInfo', ['channel', 'pre_commands', 'to_complete',
                                 'cursor_pos', 'before_cursor', 'after_cursor'])

last_key = None
last_boxinfo = None
last_completed = ''


def get_inputbox_infos():
    inputbox = hexchat.get_info('inputbox')
    channel = hexchat.get_info('channel')

    if not inputbox.strip():
        return

    if not inputbox.lower().startswith(('/znc ', '/msg *')) and not channel.startswith('*'):
        return

    cursor_pos = hexchat.get_prefs('state_cursor')
    before_cursor = inputbox[:cursor_pos]
    after_cursor = inputbox[cursor_pos:]

    parts = before_cursor.split(' ')
    if not parts:
        return

    to_complete = parts[-1]
    before_cursor = ' '.join(parts[:-1])
    pre_commands = before_cursor.split()

    if to_complete.startswith('*') and inputbox.lower().startswith(('/msg ', '/znc ')):
        # autocomplete channel/znc module
        pre_commands.pop(0)
        print('autocomplete module: ', [pre_commands, before_cursor, to_complete, after_cursor])
        return

    # determine current module name and possibly already complete commands
    if inputbox.lower().startswith(('/msg *', '/znc *')):
        pre_commands = before_cursor.split()[2:]
        channel = before_cursor.split()[1]
    elif inputbox.lower().startswith('/znc '):
        pre_commands = before_cursor.split()[1:]
        channel = '*status'
    elif inputbox.startswith('/'):
        # any other command
        return

    return BoxInfo(channel, pre_commands, to_complete, cursor_pos, before_cursor, after_cursor)


def key_press(word, word_eol, userdata):
    global last_key, last_boxinfo, last_completed
    key, state, key_str, length = word
    key = int(key)
    state = int(state)
    length = int(length)

    if key != KEY_TAB:
        last_key = key
        return

    if last_key == KEY_TAB and last_boxinfo is not None:
        # tab is repeated, so we use the last save box info again
        boxinfo = last_boxinfo
    else:
        boxinfo = get_inputbox_infos()
        last_boxinfo = boxinfo
    last_key = key

    if not boxinfo:
        return

    commands = COMMANDS.get(boxinfo.channel, {})

    while True:
        for cmd in boxinfo.pre_commands:
            case_map = {k.lower(): k for k in commands}
            commands = commands.get(case_map.get(cmd.lower(), ''), {})
            if callable(commands):
                commands = commands(boxinfo)
                if commands is None:
                    commands = {}

        candidates = [cmd for cmd in commands if cmd.lower().startswith(boxinfo.to_complete.lower())]
        candidates.sort(key=str.lower)

        if not isinstance(commands, OptionalDict) or candidates:
            break
        elif isinstance(commands, OptionalDict) and not candidates:
            commands = commands.get_subcommand(boxinfo)

    if not candidates:
        return

    if len(candidates) == 1:
        candidate = candidates[0]
        last_key = None  # so we can jump right ahead to next subcommand
    elif 1 < len(candidates) <= 5:
        if not last_completed or last_completed not in candidates:
            candidate = candidates[0]
        else:
            index = (candidates.index(last_completed) + 1) % len(candidates)
            candidate = candidates[index]
        last_completed = candidate
    else:
        print(' '.join(candidates))
        return

    # autocomplete
    textparts = []
    if boxinfo.before_cursor:
        textparts.append(boxinfo.before_cursor)
    textparts.append(candidate)
    if boxinfo.after_cursor:
        textparts.append(boxinfo.after_cursor)
    else:
        textparts.append('')
    new_text = ' '.join(textparts)
    shift_cursor = boxinfo.cursor_pos + (len(candidate) - len(boxinfo.to_complete)) + 1
    hexchat.command('SETTEXT {}'.format(new_text))
    hexchat.command('SETCURSOR {}'.format(shift_cursor))


class OptionalDict(dict):

    def __init__(self, *args, _command=None, _next=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._next = _next
        self._command = _command

    def __repr__(self):
        return 'OptionalDict({!r})'.format(super().__repr__())

    def get_subcommand(self, *args, **kwargs):
        return {self._command: self._next(*args, **kwargs)}


def help_getter(boxinfo: BoxInfo):
    return {k: {} for k in COMMANDS.get(boxinfo.channel, {})}


def module_getter(boxinfo: BoxInfo):
    return {k[1:]: {} for k in COMMANDS}


COMMANDS = {
    '*status': {
        'HELP': help_getter,
        'Version': {},
        'ListMods': {},
        'ListAvailMods': {},
        'ListNicks': {},
        'ListServers': {},
        'AddNetwork': {},
        'DelNetwork': {},
        'ListNetworks': {},
        'MoveNetwork': {},
        'JumpNetwork': {},
        'AddServer': {},
        'DelServer': {},
        'AddTrustedServerFingerprint': {},
        'DelTrustedServerFingerprint': {},
        'ListTrustedServerFingerprints': {},
        'EnableChan': {},
        'DisableChan': {},
        'Detach': {},
        'Topics': {},
        'PlayBuffer': {},
        'ClearBuffer': {},
        'ClearAllChannelBuffers': {},
        'ClearAllQueryBuffers': {},
        'SetBuffer': {},
        'AddBindHost': {},
        'DelBindHost': {},
        'ListBindHosts': {},
        'SetBindHost': {},
        'SetUserBindHost': {},
        'ClearBindHost': {},
        'ClearUserBindHost': {},
        'ShowBindHost': {},
        'Jump': {},
        'Disconnect': {},
        'Connect': {},
        'Uptime': {},
        'LoadMod': OptionalDict({
            '--type=global': module_getter,
            '--type=user': module_getter,
            '--type=network': module_getter,
        }, _command='LoadMod', _next=module_getter),
        'UnloadMod': OptionalDict({
            '--type=global': module_getter,
            '--type=user': module_getter,
            '--type=network': module_getter,
        }, _command='UnloadMod', _next=module_getter),
        'ReloadMod': OptionalDict({
            '--type=global': module_getter,
            '--type=user': module_getter,
            '--type=network': module_getter,
        }, _command='ReloadMod', _next=module_getter),
        'UpdateMod': module_getter,
        'ShowMOTD': {},
        'SetMOTD': {},
        'AddMOTD': {},
        'ClearMOTD': {},
        'ListPorts': {},
        'AddPort': {},
        'DelPort': {},
        'Rehash': {},
        'SaveConfig': {},
        'ListUsers': {},
        'ListAllUserNetworks': {},
        'ListChans': {},
        'ListClients': {},
        'Traffic': {},
        'Broadcast': {},
        'Shutdown': {},
        'Restart': {},
    },
}

hexchat.hook_print('Key Press', key_press)
