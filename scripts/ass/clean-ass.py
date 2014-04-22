#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
import re
import argparse
import random
import hashlib

import ass

desired_fields = ('ScriptType', 'PlayResX', 'PlayResY', 'WrapStyle',
                  'ScaledBorderAndShadow', 'YCbCr Matrix')
tag_re = re.compile(r'\{[^\\]*\}')
spaces_re = re.compile(r'\s{2,}')
dots_re = re.compile(r'(\.{3})')
quotes_re = re.compile(r'"([^"]*)"')


def clean_text(event, replace_quotes=False):
    text = tag_re.sub('', event.text).strip()
    text = spaces_re.sub(' ', text)
    text = dots_re.sub('…', text)
    if replace_quotes:
        text = quotes_re.sub(r'„\1“', text)
    event.text = text
    return event


def main(args):

    with open(args.filename, 'r') as f:
        doc = ass.parse(f)

    known = set(style.name for style in doc.styles)
    used = set(event.style for event in doc.events if event.text.strip() != '')
    unknown = used - known
    if unknown:
        raise LookupError('Some styles are not defined: {}'.format(unknown))

    # remove unused styles
    doc.styles = [style for style in doc.styles if style.name in used]

    # rename styles to random names
    if args.rename:
        prefix = hex(random.getrandbits(128))[-8:]

        style_names = {}
        _new_names = set()
        for style in doc.styles:
            while True:
                new_name = hex(random.getrandbits(128))[-8:]
                if new_name not in _new_names:
                    _new_names.add(new_name)
                    break
            style_names[style.name] = '{}-{}'.format(prefix, new_name)

        for style in doc.styles:
            style.name = style_names[style.name]

    # clean up events and remove comments or empty texts.
    events = doc.events
    events = (clean_text(event, args.quotes) for event in events)
    events = (event for event in events if event.text != ''
              and event.TYPE.lower() == 'dialogue')
    doc.events = list(events)

    # rename the styles used in events.
    if args.rename:
        for event in doc.events:
            event.style = style_names[event.style]

    # remove all the third party tools headers (Aegisub etc.)
    fields = doc.fields.items()
    fields = ((k, v) for k, v in fields if k in desired_fields)
    doc.fields = dict(fields)
    if args.title is not None:
        doc.fields['Title'] = args.title

    # dump script
    with open(args.output, 'w') as f:
        doc.dump_file(f)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-t', dest='title', type=str,
        help='Sets the ASS scripts title.')

    parser.add_argument(
        '-o', dest='output', type=str, default='output.ass',
        help='Specify the ASS output file.')

    parser.add_argument(
        '-s', dest='rename', action='store_true',
        help='If set, the style names are renamed to random '
             '(but unique) names.')

    parser.add_argument(
        '-q', dest='quotes', action='store_true',
        help='If set, " and \' quotation marks are replaced with proper ones.')

    parser.add_argument('filename', type=str, help='Input ASS file.')

    args = parser.parse_args()
    main(args)
