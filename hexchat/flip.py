
__module_name__ = "Flip"
__module_version__ = "0.2"
__module_description__ = "Flips text upside down."

import hexchat
hexchat.emit_print("Generic Message", "Loading", "{} {} - {}".format(
                   __module_name__, __module_version__,
                   __module_description__))

source = '!"\'(),./0123456789<>?ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]_'\
         'abcdefghijklmnopqrstuvwxyz{}‘’‚“”„'
target = '¡„‚)(‘˙\\0ꞁ2Ɛ459786><¿∀BↃD∃Ⅎ⅁HIſK⅂WNOԀΌRS⊥⋂ΛMX⅄Z]/[‾'\
         'ɐqɔpǝɟᵷɥᴉɾʞꞁɯuodbɹsʇnʌʍxʎz}{‚‚‘„„“'

assert len(source) == len(target)

flip_table = str.maketrans(source, target)


def fliptext(text):
    return text[::-1].strip().translate(flip_table)


def flip(word, word_eol, userdata):

    if len(word) <= 1:
        return hexchat.EAT_NONE

    text = fliptext(word_eol[1])
    cmd = word[0].lower()

    if cmd == 'flip':
        hexchat.command('say (╯°□°)╯︵ ' + text)
    elif cmd == 'loveflip':
        hexchat.command('say (ノ♥‿♥)ノ︵ ' + text)
    elif cmd == 'happyflip':
        hexchat.command('say (ノ^_^)ノ︵ ' + text)
    elif cmd == 'coolflip':  # deal with it
        hexchat.command('say (ノ■_■)ノ︵ ' + text)
        # hexchat.command('say (⌐■_■)ノ︵ ' + text)

    return hexchat.EAT_HEXCHAT


def putback(word, word_eol, userdata):
    if len(word) <= 1:
        return hexchat.EAT_NONE

    text = word_eol[1].strip()
    hexchat.command('say {}◡ﾉ(° -°ﾉ) sry..'.format(text))


hexchat.hook_command('FLIP', flip)
hexchat.hook_command('LOVEFLIP', flip)
hexchat.hook_command('HAPPYFLIP', flip)
hexchat.hook_command('COOLFLIP', flip)
hexchat.hook_command('PUTBACK', putback)
