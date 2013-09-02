# -*- coding: utf-8 -*-

__module_name__ = "MPD np-script"
__module_version__ = "1.0"
__module_description__ = "Displayes the current song using the /np command"

import xchat
from os import path
from mpd import MPDClient

import httplib
from urllib2 import urlparse
import json

def trydecode(s, charsets=None):
    if charsets is None:
        charsets = ['utf-8', 'latin1']
    
    for c in charsets:
        try:
            tmps = s.decode(c)
        except:
            pass
        else:
            return tmps
    raise UnicodeDecodeError('No charset matched.')


def get_youtube_string():
    
    # started chromium with cmd arg "--remote-debugging-port=9221"
    # it's ugly, but works for now. Be sure to be behind a firewall
    try:
        h = httplib.HTTPConnection('localhost:9221', timeout=2)
        h.request('GET', '/json')
        r = h.getresponse()
        body = r.read()
        data = json.loads(body)
    except:
        return None
    
    for tab in data:
        if tab['url'].startswith(u'http://www.youtube.com/') or tab['url'].startswith(u'https://www.youtube.com/'):
            if tab['title'].startswith(u'▶ '):
                up = urlparse.urlparse(tab['url'])
                params = up.query.split('&')
                yurl = None
                for param in params:
                    name, _, value = param.partition('=')
                    name = name.strip()
                    value = value.strip()
                    if name == 'v' and value != '':
                        yurl = u'youtu.be/{}'.format(value)
                
                tabtitle = tab['title'][2:]
                if tabtitle.endswith(u' - YouTube'):
                    tabtitle = tabtitle[:-10]
                
                if yurl is not None:
                    return u'{0} ({1})'.format(tabtitle, yurl)
                else:
                    return u'{0}'.format(tabtitle)
    
    return None
    
def get_mpd_string():
    
    c = MPDClient()
    c.timeout = 2
    c.connect('localhost', 6600)
    
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
            filename = trydecode(filename)
            filename = path.basename(filename).replace('_', ' ')
            filename, _, ext = filename.rpartition('.')
            if filename == '':
                filename = ext
            metalist.append(filename)
    else:
        if artist is not None:
            metalist.append(trydecode(artist))
        if album is not None:
            metalist.append(trydecode(album))
        if title is not None:
            metalist.append(trydecode(title))
    
    if len(metalist) == 0:
        xchat.prnt('Keine Metadaten gefunden.')
        return
    
    metastr = u' - '.join(metalist)
    
    seconds = int(song.get('time', None))
    minutes = seconds // 60
    seconds = seconds % 60
    
    d = {'meta': metastr, 'sec': seconds, 'min': minutes}
    metastr = u'{meta} - {min}:{sec:02d}'.format(**d)
    
    return metastr


def np(word, word_eol, userdata):
    
    metastr = get_mpd_string()
    if metastr is None:
        metastr = get_youtube_string()
    
    if metastr is None:
        xchat.prnt('Es wird zur zeit nichts abgespielt.')
        return
    
    
    outputstr = u'♫ {} ♫'.format(metastr)
    xchat.command('me is listening to: {}'.format(outputstr.encode('utf-8')))
    

xchat.hook_command("NP", np, help="/NP Displays the current song if MPD is playing.")

