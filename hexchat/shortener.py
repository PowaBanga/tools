
__module_name__ = "shortener"
__module_version__ = "0.1"
__module_description__ = "Shortens a URL using bit.ly"
__module_author__ = "knitori"

import hexchat
import urllib.request
import urllib.parse
import json

# To get your username and API Key, login at bit.ly and follow this link:
# https://bitly.com/a/your_api_key

# Note: the API-key mechanism is deprecated and might
# get removed in the future in favour of more modern authentication
# methods like OAuth. So this script might break in the future.

USERNAME = 'your username'
API_KEY = 'your api key'


def shorten(word, word_eol, userdata):
    params = {
        'version': '2.0.1',
        'login': USERNAME,
        'apiKey': API_KEY,
        'longUrl': word[1],
        'format': 'json',
    }
    urlparts = ('https', 'api-ssl.bit.ly', '/shorten',
                urllib.parse.urlencode(params), '')
    url = urllib.parse.urlunsplit(urlparts)
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    data = json.loads(response.read().decode('utf-8'))
    if data['errorCode'] != 0 or data['errorMessage']:
        hexchat.emit_print('Generic Message', '*', '\x0304An error occured:')
        hexchat.emit_print('Generic Message', '*', '\x0304({}) {}'.format(
            data['errorCode'], data['errorMessage']))
        return hexchat.EAT_HEXCHAT

    short_url = None
    for url in data['results']:
        short_url = data['results'][url].get('shortUrl', None)

    if short_url is not None:
        hexchat.prnt('Shortened URL: {}'.format(short_url))
        return hexchat.EAT_HEXCHAT

    hexchat.prnt('Shortening failed!')
    return hexchat.EAT_HEXCHAT


hexchat.hook_command('SHORTEN', shorten)
hexchat.hook_command('SHORT', shorten)

hexchat.prnt('Shortener succesfully loaded.')
