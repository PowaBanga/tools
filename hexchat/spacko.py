# -*- coding: utf-8 -*-

# Python 2.7 Module
# HexChat 2.9.5

__module_name__ = "Spacko Script"
__module_version__ = "1.0"
__module_description__ = "Spacko Spacko Spacko /spacko"

import xchat
import random
import time

def spacko(word, word_eol, userdata):
    
    random.seed(time.time())
    
    l = [
        u'Ist der Hund kugelrund, frisst er Spacko, wie ein Schlund!',
        u'Frisst Ihr Hund Spacko-Futter, wird er selbst zu Spacko-Futter!',
        u'Spacko-Futter für den Hund, da gehts dem ganzen Hund gesund!',
        u'Kauft Spacko-Futter für euren Spacko-Hund!',
        u'Spacko, Spacko, Spacko-Hund, und schnell in meinem Mund!'
    ]
    
    spacko_string = l[random.randrange(len(l))]
    
    xchat.command('say »{}«'.format(spacko_string))
    

xchat.hook_command("SPACKO", spacko, help="/SPACKO")

