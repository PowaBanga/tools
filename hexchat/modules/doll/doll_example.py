#!/usr/bin/env python3

import re
import os
import sys
import hexchat

# add module path like this for now
include_path = os.path.join(
    hexchat.get_info("configdir"), 'addons', 'pymodules')
sys.path.insert(0, include_path)

__module_name__ = "cmdtest"
__module_version__ = "0.1.0"
__module_description__ = "foobar"

from doll import prefixed
from doll import Integer, Date, Time, String

command = prefixed('!')
date_format = re.compile(
    r'^(?P<day>\d{1,2}).(?P<month>\d{1,2}).(?P<year>(?:\d{2}|\d{4}))$')


@command.error_handler
def test_command(exception):
    ctx = hexchat.get_context()
    ctx.command("say ein fehler ist aufgetreten: {!s}".format(exception))


@command
def test_command(name: String(3, 10), birthday: Date(date_format)):
    ctx = hexchat.get_context()
    ctx.command('say success: {!r}'.format((name, birthday)))
