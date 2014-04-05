#!/usr/bin/env python3.4
# -*- encoding: utf-8 -*-

import requests
import bs4
import re
import io
from contextlib import closing
from PIL import Image

import logging
logger = logging.getLogger('fetch-url-title.py')

"""
url_pattern = re.compile(r'''
    (?:
        (?P<p1>\() | (?P<p2>\{) | (?P<p3>\<)
      | (?P<p4>\[) | (?P<p5>") | (?P<p6>')
    )?
        (?P<url>https?://\S+)
    (?(p6)')(?(p5)")(?(p4)\])(?(p3)\>)(?(p2)\})(?(p1)\))
''', re.X)
"""


# snippet from http://stackoverflow.com/questions/1094841/reusable-library-to-
#    get-human-readable-version-of-file-size/1094933#1094933
def sizeof_fmt(num):
    for x in ['bytes', 'KiB', 'MiB', 'GiB']:
        if num < 1024.0 and num > -1024.0:
            return "{:3.1f} {}".format(num, x)
        num /= 1024.0
    return "{:3.1f} {}".format(num, 'TiB')


def request_url(url):
    logger.info('Requested {!r}'.format(url))
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHT'
                      'ML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
    }
    response = requests.get(url, headers=headers, allow_redirects=True,
                            stream=True)

    MAX_LENGTH = 16 << 10

    with closing(response) as r:
        for content in r.iter_content(1024, decode_unicode=True):
            try:
                page_content += content
            except:
                page_content = content
            if len(page_content) >= MAX_LENGTH:
                break

    # each element will be delimited by <delimeter>
    info_strings = []
    delimeter = ' | '

    content_type = response.headers.get('content-type', '')
    if content_type.startswith('text/html'):
        # HTML Webpage
        soup = bs4.BeautifulSoup(page_content)
        if soup.title is None:
            return
        title = re.sub(r'\s{2,}', ' ', soup.title.string).strip()
        if title.endswith(' - YouTube'):
            title = title[:-10].strip()
        info_strings.append(title)

    elif content_type.startswith('image/'):
        # Images
        b = io.BytesIO(page_content)
        # print(page_content[:100])
        # note: might raise an exception. just let it happen
        im = Image.open(b)

        w, h = im.size
        mime = 'image/' + im.format.lower()
        info_strings.append(mime)
        info_strings.append('{}x{}'.format(w, h))
        size = response.headers.get('content-length', None)
        if size is not None:
            info_strings.append('size {}'.format(
                sizeof_fmt(int(size))))

    if info_strings:
        # build the output info_string
        if response.history:
            redirect_string = '{} redirect{}: {}'.format(
                len(response.history),
                '' if len(response.history) == 1 else 's',
                response.url)
            info_strings = [redirect_string] + info_strings

        info_string = delimeter.join(info_strings)
        return info_string
    return None


def main():
    import sys
    if len(sys.argv) <= 1:
        sys.exit(2)

    url = sys.argv[1]
    info_string = request_url(url)
    if info_string is None:
        sys.exit(1)

    sys.stdout.write('{}\n'.format(info_string))
    sys.stdout.flush()
    sys.exit(0)

if __name__ == '__main__':
    main()
