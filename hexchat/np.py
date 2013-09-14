# -*- coding: utf-8 -*-

# Python 3.3 Module
# Chromium 29.0.1547.57 (217859)
# HexChat 2.9.6

__module_name__ = "MPD np-script"
__module_version__ = "1.1"
__module_description__ = "Displayes the current song using the /np command"

import hexchat

hexchat.emit_print("Generic Message", "Loading", "{} {} - {}".format(__module_name__, __module_version__, __module_description__))

from mpd import MPDClient

import os
import json
import http.client
from urllib.parse import urlparse


def get_youtube_string():
    
    # started chromium with cmd arg "--remote-debugging-port=9221"
    # it's ugly, but works for now. Be sure to be behind a firewall
    try:
        h = http.client.HTTPConnection('localhost:9221', timeout=2)
        h.request('GET', '/json')
        r = h.getresponse()
        body = r.read()
        data = json.loads(body.decode('ascii'))
    except:
        return None
    
    for tab in data:
        if tab['url'].startswith('http://www.youtube.com/') or tab['url'].startswith('https://www.youtube.com/'):
            if tab['title'].startswith('▶ '):
                up = urlparse(tab['url'])
                params = up.query.split('&')
                yurl = None
                for param in params:
                    name, _, value = param.partition('=')
                    name = name.strip()
                    value = value.strip()
                    if name == 'v' and value != '':
                        yurl = 'youtu.be/{}'.format(value)
                
                tabtitle = tab['title'][2:]
                if tabtitle.endswith(' - YouTube'):
                    tabtitle = tabtitle[:-10]
                
                if yurl is not None:
                    return '{0} ({1})'.format(tabtitle, yurl)
                else:
                    return '{0}'.format(tabtitle)
    
    return None
    
def get_mpd_string():
    
    c = MPDClient()
    c.timeout = 2
    try:
        c.connect('localhost', 6600)
    except:
        return None
    
    status = c.status()
    
    if status['state'] != 'play':
        return None
    
    metalist = []
    song = c.currentsong()
    
    artist = song.get('artist', None)
    title = song.get('title', None)
    album = song.get('album', None)
    if artist is None and title is None and album is None:
        filename = song.get('file', None)
        if filename is not None:
            filename = filename
            filename = os.path.basename(filename).replace('_', ' ')
            filename, _, ext = filename.rpartition('.')
            if filename == '':
                filename = ext
            metalist.append(filename)
    else:
        if artist is not None:
            metalist.append(artist)
        if album is not None:
            metalist.append(album)
        if title is not None:
            metalist.append(title)
    
    if len(metalist) == 0:
        hexchat.prnt('Keine Metadaten gefunden.')
        return
    
    metastr = ' - '.join(metalist)
    
    seconds = int(song.get('time', None))
    minutes = seconds // 60
    seconds = seconds % 60
    
    d = {'meta': metastr, 'sec': seconds, 'min': minutes}
    metastr = '{meta} - {min}:{sec:02d}'.format(**d)
    
    return metastr


def np(word, word_eol, userdata):
    
    metastr = get_mpd_string()
    if metastr is None:
        metastr = get_youtube_string()
    
    if metastr is None:
        hexchat.prnt('Es wird zur zeit nichts abgespielt.')
        return
    
    outputstr = '♫ {} ♫'.format(metastr)
    hexchat.command('me is listening to: {}'.format(outputstr))
    return hexchat.EAT_XCHAT
    

hexchat.hook_command("NP", np, help="/NP Displays the current song if MPD is playing.")


