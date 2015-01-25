#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from __future__ import print_function

import re
import sys
from urllib.parse import urlparse, parse_qs

import requests
import bs4


MAX_URL_LENGTH = 128


def debug(*args):
    print(*args, file=sys.stderr)


def main(search):
    # /search?
    # safe=off
    # &authuser=0
    # &site=webhp
    # &source=hp
    # &q=test
    # &oq=test
    params = {
        'safe': 'off',
        'q': search,
        'oq': search,
        'site': 'webhp',
        'source': 'hp',
    }
    response = requests.get(
        'https://www.google.com/search', params=params)

    soup = bs4.BeautifulSoup(response.text)
    h3_list = soup.findAll('h3', **{'class': 'r'})

    url_list = []

    for h3 in h3_list:
        url = urlparse(h3.a['href'])
        query = parse_qs(url.query)

        if 'q' in query and query['q']:
            q_url = query['q'][0]
        elif 'url' in query and query['url']:
            q_url = query['url'][0]

        if '://' in q_url and len(q_url) <= MAX_URL_LENGTH:
            url_list.append(q_url)
            if len(url_list) == 3:
                break

    if url_list:
        print(' \x02\x0304|\x03\x02 '.join(url_list))
        sys.exit(0)

    sys.exit(2)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.exit(1)
    main(sys.argv[1])
