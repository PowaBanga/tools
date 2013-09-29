# -*- coding: utf-8 -*-

# Python 3.3 Module
# HexChat 2.9.6

__module_name__ = "Spacko Script"
__module_version__ = "1.0"
__module_description__ = "Spacko Spacko Spacko /spacko"

import hexchat

hexchat.emit_print("Generic Message", "Loading", "{} {} - {}".format(__module_name__, __module_version__, __module_description__))

import random
import time

def spacko(word, word_eol, userdata):
    
    random.seed(time.time())
    
    l = [
        'Ist der Hund kugelrund, frisst er Spacko, wie ein Schlund!',
        'Frisst Ihr Hund Spacko-Futter, wird er selbst zu Spacko-Futter!',
        'Spacko-Futter für den Hund, da gehts dem ganzen Hund gesund!',
        'Kauft Spacko-Futter für euren Spacko-Hund!',
        'Spacko, Spacko, Spacko-Hund, und schnell in meinem Mund!'
    ]
    
    spacko_string = l[random.randrange(len(l))]
    
    hexchat.command('say »{}«'.format(spacko_string))
    return hexchat.EAT_HEXCHAT

hexchat.hook_command("SPACKO", spacko, help="/SPACKO")

