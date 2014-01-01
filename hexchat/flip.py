
__module_name__ = "Flip"
__module_version__ = "0.1"
__module_description__ = "Flips text upside down."

import hexchat
hexchat.emit_print("Generic Message", "Loading", "{} {} - {}".format(
                   __module_name__, __module_version__,
                   __module_description__))

flipdict = {
    'a': 'ɐ', 'A': '\N{FOR ALL}',
    'b': 'q', 'B': 'B',  # missing
    'c': 'ɔ', 'C': 'Ↄ',
    'd': 'p', 'D': 'D',  # missing
    'e': 'ǝ', 'E': '\N{THERE EXISTS}',
    'f': 'ɟ', 'F': 'Ⅎ',
    'g': 'ᵷ', 'G': '⅁',
    'h': 'ɥ', 'H': 'H',
    'i': 'ᴉ', 'I': 'I',
    'j': 'ɾ', 'J': 'ſ',
    'k': 'ʞ', 'K': 'K',  # missing
    'l': 'ꞁ', 'L': '\N{TURNED SANS-SERIF CAPITAL L}',
    'm': 'ɯ', 'M': 'W',
    'n': 'u', 'N': 'N',
    'o': 'o', 'O': 'O',
    'p': 'd', 'P': 'Ԁ',
    'q': 'b', 'Q': 'Ό',
    'r': 'ɹ', 'R': 'R',  # missing
    's': 's', 'S': 'S',
    't': 'ʇ', 'T': '\N{UP TACK}',
    'u': 'n', 'U': '\N{N-ARY INTERSECTION}',
    'v': 'ʌ', 'V': '\N{GREEK CAPITAL LETTER LAMDA}',
    'w': 'ʍ', 'W': 'M',
    'x': 'x', 'X': 'X',
    'y': 'ʎ', 'Y': '⅄',
    'z': 'z', 'Z': 'Z',
    '.': '\u0002˙\u000F',
    ',': '‘', '0': '0',
    '?': '¿', '1': 'ꞁ',
    '!': '¡', '2': '2',  # missing
    '„': '“', '3': 'Ɛ',
    '“': '„', '4': '4',  # missing
    '”': '„', '5': '5',  # missing
    '"': '„', '6': '9',
    '‚': '‘', '7': '7',  # missing
    '‘': '‚', '8': '8',
    '‘': '‚', '9': '6',
    '’': '‚',
    "'": '‚',
    '/': '\\',
    '\\': '/',
    '_': '\N{OVERLINE}',
    '(': ')',
    ')': '(',
    '{': '}',
    '}': '{',
    '[': ']',
    ']': '[',
    '<': '>',
    '>': '<',
}


def fliptext(text):
    text = text[::-1].strip()
    newtext = ''
    for c in text:
        newtext += flipdict.get(c, c)
    return newtext


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
        #hexchat.command('say (⌐■_■)ノ︵ ' + text)

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
