"""
Rename hexchat.pyi and add to your IDEs (e.g. PyCharm) Project to get
autocomplete for hexchat API.

Assumes at least Python 3.5

http://img.xrmb2.net/images/940180.png
"""

import enum
import typing as t


class _Priority(enum.Enum):
    PRI_HIGHEST = 127
    PRI_HIGH = 64
    PRI_NORM = 0
    PRI_LOW = -64
    PRI_LOWEST = -128


class _EatEnum(enum.Enum):
    EAT_NONE = 0
    EAT_HEXCHAT = 1
    EAT_PLUGIN = 2
    EAT_ALL = EAT_HEXCHAT | EAT_PLUGIN


PRI_HIGHEST = _Priority.PRI_HIGHEST
PRI_HIGH = _Priority.PRI_HIGH
PRI_NORM = _Priority.PRI_NORM
PRI_LOW = _Priority.PRI_LOW
PRI_LOWEST = _Priority.PRI_LOWEST


EAT_NONE = _EatEnum.EAT_NONE
EAT_HEXCHAT = _EatEnum.EAT_HEXCHAT
EAT_PLUGIN = _EatEnum.EAT_PLUGIN
EAT_ALL = _EatEnum.EAT_ALL


class ChannelItem:
    channel = str
    channelkey = str
    chanmodes = str
    chantypes = str
    context = t.Any
    id = str
    lag = int
    maxmodes = int
    network = str
    nickprefixes = str
    nickmodes = str
    queue = int
    server = str
    users = int
    type = int
    flags = int


class DccItem:
    address32 = int
    cps = int
    destfile = str
    file = str
    nick = str
    port = int
    pos = int
    resume = int
    size = int
    status = int
    type = int


class UserItem:
    account = str
    away = str
    host = str
    lasttalk = int
    nick = str
    prefix = str
    realname = str
    selected = str


class IgnoreItem:
    mask = str
    flags = int


class NotifyItem:
    nick = str
    networks = t.Any
    flags = int
    on = int
    off = int
    seen = int


ChannelList = t.List[ChannelItem]
DccList = t.List[DccItem]
UserList = t.List[UserItem]
IgnoreList = t.List[IgnoreItem]
NotifyList = t.List[NotifyItem]


def prnt(string: str) -> None:
    pass


def emit_print(event_name: str, *args: str) -> None:
    pass


def command(string: str) -> None:
    pass


def nickcmp(s1: str, s2: str) -> int:
    pass


def strip(text: str, length: int=-1, flags: int=3) -> str:
    pass


def get_info(type: str) -> t.Union[str, None]:
    pass


def get_prefs(name: str) -> t.Union[str, int]:
    pass


def get_list(type: str) -> t.Union[ChannelList, DccList, UserList, IgnoreList, NotifyList]:
    pass


class Context:
    def set(self):
        pass

    def prnt(self, string: str) -> None:
        pass

    def emit_print(self, event_name: str, *args: str) -> None:
        pass

    def command(self, string: str) -> None:
        pass

    def get_info(self, type: str) -> t.Union[str, None]:
        pass

    def get_list(self, type: str) -> \
            t.Union[ChannelList, DccList, UserList, IgnoreList, NotifyList]:
        pass


class HookHandler(int):
    pass


def hook_command(name: str, callback: t.Callable, userdata: t.Any=None,
                 priority: _Priority=PRI_NORM, help: str=None) -> HookHandler:
    pass


def hook_print(name: str, callback: t.Callable, userdata: t.Any=None,
               priority: _Priority=PRI_NORM, help: str=None) -> HookHandler:
    pass


def hook_print_attrs(name: str, callback: t.Callable, userdata: t.Any=None,
                     priority: _Priority=PRI_NORM, help: str=None) -> HookHandler:
    pass


def hook_server(name: str, callback: t.Callable, userdata: t.Any=None,
                priority: _Priority=PRI_NORM, help: str=None) -> HookHandler:
    pass


def hook_server_attrs(name: str, callback: t.Callable, userdata: t.Any=None,
                      priority: _Priority=PRI_NORM, help: str=None) -> HookHandler:
    pass


def hook_timer(timeout: int, callback: t.Callable, userdata: t.Any=None) -> HookHandler:
    pass


def hook_unload(callback: t.Callable, userdata: t.Any=None) -> HookHandler:
    pass


def unhook(handler: HookHandler) -> None:
    pass


def set_pluginpref(name: str, value: t.Union[int, str]) -> bool:
    pass


def get_pluginpref(name: str) -> t.Union[int, str, None]:
    pass


def del_pluginpref(name: str) -> bool:
    pass


def list_pluginpref() -> t.List[str]:
    pass


def get_context() -> Context:
    pass
