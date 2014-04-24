#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import sys
import json
from subprocess import Popen, PIPE, DEVNULL
from collections import namedtuple
import difflib

import ass

Ass = namedtuple('Ass', 'filename data')
Video = namedtuple('Video', 'filename data')


class FileData:
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data

    def __lt__(self, other):
        return str(self).lower() < str(other).lower()

    def __gt__(self, other):
        return str(self).lower() > str(other).lower()

    def __str__(self):
        return self.filename


class Ass(FileData):
    def __repr__(self):
        return '<Ass filename={!r} styles={} events={}>'\
            .format(self.filename, len(self.data.styles),
                    len(self.data.events))


class Video(FileData):
    def __repr__(self):
        infos = {}
        for stream in self.data['streams']:
            ct = stream['codec_type']
            infos[ct] = infos.get(ct, 0) + 1
        return '<Video filename={!r} streams={}>'\
            .format(self.filename, infos)

    @property
    def start_time(self):
        for stream in self.data['streams']:
            if stream['codec_type'] == 'video':
                return float(stream['start_time'])
        return 0.0


class Collection(list):
    def __init__(self, args, name=None):
        self.name = name
        super().__init__(args)

    def __repr__(self):
        if self.name is None:
            outstr = '\n'
        else:
            outstr = '\n{}\n'.format(self.name)
        for i, item in enumerate(self):
            outstr += '  * {:.>3d} {}\n'.format(i, str(item))
        return outstr


def get_fonts(fontdir, recursive=False, extensions=None):
    if extensions is None:
        extensions = ('.ttf', '.otf', '.ttc')
    font_list = []
    for path, dirs, files in os.walk(fontdir):
        font_list += [
            os.path.join(path, filename) for filename in files
            if filename.lower().endswith(extensions)]
        if not recursive:
            break
    return font_list


def diff(ass1, ass2):
    with open(ass1.filename, 'r') as f:
        lines1 = list(f)

    with open(ass2.filename, 'r') as f:
        lines2 = list(f)

    lines = difflib.unified_diff(lines1, lines2, ass1.filename, ass2.filename)
    for line in lines:
        if line[0] == ' ':
            print(line, end='')
        elif line[0] == '+':
            print('\033[32m{}\033[0m'.format(line), end='')
        elif line[0] == '-':
            print('\033[31m{}\033[0m'.format(line), end='')
        else:
            print('\033[37m{}\033[0m'.format(line), end='')


def rename_style(doc, style_name, new_style_name):
    for style in doc.styles:
        if style.name == style_name:
            style.name = new_style_name
    for event in doc.events:
        if event.style == style_name:
            event.style = new_style_name


def save_ass(doc, filename):
    with open(filename, 'w') as f:
        doc.dump_file(f)


def join(*ass_objects):
    newdoc = ass.document.Document()
    style_names = set()

    fields = {
        'PlayResX': set(),
        'PlayResY': set(),
        'ScaledBorderAndShadow': set(),
    }

    newdoc.events = []
    newdoc.styles = []

    print('Merging...')
    for i, ass_object in enumerate(ass_objects):
        print('   * {}'.format(ass_object.filename))
        doc = ass_object.data
        for name in fields:
            if name in doc.fields:
                fields[name].add(doc.fields[name])

        for style in doc.styles:
            i = 2
            while style.name in style_names:
                rename_style(doc, style.name, '{} ({})'.format(style.name, i))
                i += 1
            style_names.add(style.name)
        used_styles = set(event.style for event in doc.events)

        for event in doc.events:
            if event.text.strip() != '':
                newdoc.events.append(event)

    used_styles = set(event.style for event in newdoc.events)
    newdoc.styles = []
    for a in ass_objects:
        for style in a.data.styles:
            if style.name in used_styles:
                newdoc.styles.append(style)

    newdoc.styles.sort(key=lambda item: item.name.lower())

    newdoc.fields = {}
    newdoc.fields['ScriptType'] = 'v4.00+'

    if len(fields['PlayResX']) != 1 or len(fields['PlayResY']) != 1:
        # todo: deal with different resolutions. for now exception
        raise ValueError('ASS files have different resolutions')
    else:
        newdoc.fields['PlayResX'] = list(fields['PlayResX'])[0]
        newdoc.fields['PlayResY'] = list(fields['PlayResY'])[0]

    if len(fields['ScaledBorderAndShadow']) != 1:
        raise ValueError('ASS files have different `ScaledBorderAndShadow`.')
    else:
        newdoc.fields['ScaledBorderAndShadow'] = \
            list(fields['ScaledBorderAndShadow'])[0]

    title = input('Input new ASS title: ')
    newdoc.fields['Title'] = title.strip()

    return newdoc


def load_files():
    subtitles = []
    videos = []
    for filename in os.listdir('.'):
        if filename.lower().endswith('.ass'):
            with open(filename, 'r') as f:
                subtitles.append(Ass(filename, ass.parse(f)))
        elif filename.lower().endswith(('.mkv', '.mp4')):
            proc = Popen(
                ['ffprobe', '-i', filename, '-v', 'quiet', '-print_format',
                 'json', '-show_streams'], stdout=PIPE, stderr=DEVNULL)
            out, err = proc.communicate()
            proc.wait()
            data = json.loads(out.decode('ascii'))
            videos.append(Video(filename, data))

    videos.sort()
    subtitles.sort()
    videos = Collection(videos, 'Video files')
    subtitles = Collection(subtitles, 'ASS files')
    return subtitles, videos


if __name__ == '__main__':
    subtitles, videos = load_files()
