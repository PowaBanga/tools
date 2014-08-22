#!/usr/bin/env python3

import os
import sys
import hexchat

include_path = os.path.join(
    hexchat.get_info("configdir"), 'addons', 'pymodules')

sys.path.insert(0, include_path)

__module_name__ = "cmdtest"
__module_version__ = "0.1.0"
__module_description__ = "foobar"

from doll import setup_command
from doll import Field, Integer
from doll.validators import Optional

Command = setup_command(prefix='!', separator='-')


class FooBar(Command):
    number = Field(Integer)
    age = Field(Integer)
    year = Field(Integer)
    value = Field(Integer, validators=[Optional])


foobar = FooBar()


@foobar.error_handler
def error(exception):
    ctx = hexchat.get_context()
    ctx.command("say ein fehler ist aufgetreten: {!s}".format(exception))


@foobar
def test(number, age, year, value, userdata):
    ctx = hexchat.get_context()
    ctx.command('say success: {!r}'.format((number, age, year, value)))
