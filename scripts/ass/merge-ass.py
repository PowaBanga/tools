#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
from collections import namedtuple
from datetime import timedelta

version_info = (0, 1, 0)

preferred_order_styles = [
    'Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour',
    'OutlineColour', 'BackColour', 'Bold', 'Italic', 'Underline', 'StrikeOut',
    'ScaleX', 'ScaleY', 'Spacing', 'Angle', 'BorderStyle', 'Outline', 'Shadow',
    'Alignment', 'MarginL', 'MarginR', 'MarginV', 'Encoding'
]

preferred_order_events = [
    'Layer', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV',
    'Effect', 'Text'
]

script_info_keys = ('Title', 'PlayResX', 'PlayResY', 'ScaledBorderAndShadow',
    'ScriptType', 'WrapStyle', 'YCbCr Matrix'
)

AssStyle = namedtuple('AssStyle', preferred_order_styles)
AssDialogue = namedtuple('AssDialogue', preferred_order_events)
AssComment = namedtuple('AssComment', preferred_order_events)
PlainComment = namedtuple('PlainComment', 'Text')


def debug_print(*args, end='\n'):
    sys.stderr.write('{}{}'.format(' '.join(map(str, args)), end))
    sys.stderr.flush()


def str2timedelta(text):
    """Converts an .ass formatted timestamp to a timedelta object"""

    if '.' in text:
        hhmmss, uu = text.split('.', 1)
        uu = int('{:<06}'.format(uu))
    else:
        hhmmss = text
        uu = 0

    hh, mm, ss = map(int, hhmmss.split(':'))
    return timedelta(hours=hh, minutes=mm, seconds=ss, microseconds=uu)


def timedelta2str(td, frac_length=2):
    """Converts a timedelta object back to an .ass formatted timestamp"""

    text = str(td)
    if '.' in text:
        hhmmss, uu = text.split('.', 1)
        return '{}.{}'.format(hhmmss, uu[0:frac_length])
    else:
        return text + '.' + ('0'*frac_length)


def copy_style(style, newname=None):
    if newname is None:
        return AssStyle(*style)
    else:
        return AssStyle(*((newname,) + style[1:]))


def copy_event(event, style):
    return AssDialogue(*(event[0:3] + (style,) + event[4:]))




class AssFile():

    def __init__(self, options=None):
        self.script_info = {}
        self.styles = {}  # [StyleName] = AssStyle
        self.events = []  # AssDialogue/AssComment elements
        self.options = options if options is not None else {}

    def _str(self, obj):
        if isinstance(obj, timedelta):
            return timedelta2str(obj)
        else:
            return str(obj)

    def load(self, f):
        """Load an .ass file. 'f' should be an opened file."""

        section_name = None
        styles_format = None
        events_format = None

        for i, line in enumerate(f):
            lineno = i+1
            line = line.strip()
            if not line or line.startswith(';'):
                continue

            if lineno == 1:
                if line.startswith('\ufeff'):
                    line = line[1:]

            if line.startswith('[') and line.endswith(']'):

                section_name = line[1:-1]
            else:
                if section_name is None:
                    # we got a non-empty line outside the first section.
                    raise ValueError('Out of section. {}'.format(line))

                if ':' not in line:
                    raise ValueError('Expected "Key: Value" tuple. Got {!r} '
                                     'instead.'.format(line))

                key, value = line.split(':', 1)
                key, value = key.strip(), value.strip()

                # for now it's all case sensitive
                if section_name in ('Script Info'):
                    # just a key=value dictionary
                    self.script_info[key] = value

                elif section_name in ('V4+ Styles', 'V4 Styles'):
                    if key == 'Format':
                        if styles_format is not None:
                            raise ValueError('"Format" already set.')
                        styles_format = list(map(str.strip, value.split(',')))
                        continue

                    if styles_format is None:
                        raise ValueError('No "Format" line found at the '
                                         'beginning')

                    if key == 'Style':
                        styles_arguments = list(
                            map(str.strip,
                                value.split(',', len(styles_format)-1)))

                        d = {}
                        for key, value in zip(styles_format, styles_arguments):
                            if value.isdigit():
                                d[key] = int(value)
                            else:
                                d[key] = value

                        ass_style = AssStyle(**d)
                        self.styles[ass_style.Name] = ass_style

                elif section_name in ('Events'):
                    if key == 'Format':
                        if events_format is not None:
                            raise ValueError('"Format" already set.')
                        events_format = list(map(str.strip, value.split(',')))
                        continue

                    if events_format is None:
                        raise ValueError('No "Format" line found at the '
                                         'beginning')

                    if key in ('Dialogue', 'Comment'):
                        events_arguments = list(
                            map(str.strip,
                                value.split(',', len(events_format)-1)))

                        d = {}
                        for ekey, evalue in zip(events_format, events_arguments):
                            if evalue.isdigit():
                                d[ekey] = int(evalue)
                            elif ekey in ('Start', 'End'):
                                d[ekey] = str2timedelta(evalue)
                                d[ekey] += timedelta(microseconds=
                                    self.options.get('sync', 0)*1000)
                            else:
                                d[ekey] = evalue

                        # don't add if Text is empty (nothing to display)
                        if d['Text'].strip() != '':
                            if key == 'Dialogue':
                                self.events.append(AssDialogue(**d))
                            else:
                                self.events.append(AssComment(**d))

                else:
                    raise ValueError(
                        'Unsopported section {!r}'.format(section_name))

    def dumps(self):

        # we collect the used style names, so we don't need to add unused
        # styles to the merged ass file.
        used_styles = set()
        for event in self.events:
            if isinstance(event, (AssDialogue, AssComment)):
                used_styles.add(event.Style)

        output = ''
        output += '[Script Info]\n'
        output += '; Generated using merge-ass.py {}\n'.format(
            '.'.join(map(str, version_info)))

        for key, value in sorted(self.script_info.items()):
            if key == 'Title' and self.options.get('title', None) is not None:
                value = self.options['title']
            output += '{}: {}\n'.format(key, value)

        output += '\n[V4+ Styles]\n'
        output += 'Format: {}\n'.format(', '.join(preferred_order_styles))
        for style_name, style in sorted(self.styles.items()):
            if style_name not in used_styles:
                # don't add unused styles
                continue
            output += 'Style: {}\n'.format(','.join(map(str, style)))

        output += '\n[Events]\n'
        output += 'Format: {}\n'.format(', '.join(preferred_order_events))
        #for event in sorted(self.events, key=lambda e: (e.Start, e.End)):
        for event in self.events:

            if isinstance(event, AssDialogue):
                output += 'Dialogue: {}\n'.format(','.join(map(self._str, event)))
            elif isinstance(event, AssComment):
                output += 'Comment: {}\n'.format(','.join(map(self._str, event)))
            elif isinstance(event, PlainComment):
                for line in event.Text.splitlines():
                    output += '; {}\n'.format(line.rstrip())


        return output




def usage():
    debug_print('Usage: {} [OPTIONS] FILENAME [ [OPTIONS] FILENAME ... ]'.format(
          sys.argv[0]))
    debug_print()
    debug_print('Options:')
    debug_print('    --sync VALUE          Adds VALUE milliseconds to every event.')
    debug_print('    --add-merge-comments  When supplied, will add some comments')
    debug_print('                          e.g. which files supplied which events.')
    debug_print('    --title VALUE         The title of the resulting .ass file.')
    debug_print()


def main(parameters, global_options):
    assfiles = []
    merged_ass = AssFile(global_options)

    debug_print('\nOpening Files:')
    for options, filename in parameters:
        debug_print('* Filename:', repr(filename))
        debug_print('* Options:')
        for key, value in options.items():
            debug_print('*     {}: {}'.format(key, value))

        input_ass = AssFile(options)
        with open(filename) as f:
            input_ass.load(f)
        assfiles.append(input_ass)

        if options.get('add-merge-comments', False):
            merged_ass.events.append(
                PlainComment('Events of file {!r}'.format(filename)))

        for key, value in input_ass.script_info.items():
            if key not in merged_ass.script_info:
                if key in script_info_keys:
                    merged_ass.script_info[key] = value

        renamed_styles = {}
        for style_name, style in input_ass.styles.items():

            # what to do when we have styles with the same name
            if style_name in merged_ass.styles:

                # since style is a namedtuple, a "==" comparison is
                # done element by element
                if style == merged_ass.styles[style_name]:
                    style = merged_ass.styles[style_name]
                else:
                    tmpname = style_name
                    n = 2
                    while tmpname in merged_ass.styles:
                        tmpname = style_name + str(n)
                        n += 1

                    renamed_styles[style.Name] = tmpname
                    style = copy_style(style, tmpname)

            else:
                style = copy_style(style)

            merged_ass.styles[style.Name] = style

        # iterate over events. change the referenced style name if necessary.
        for event in input_ass.events:
            if isinstance(event, AssDialogue):
                style_name = renamed_styles.get(event.Style, event.Style)
                event = copy_event(event, style_name)
            merged_ass.events.append(event)

        debug_print()

    sys.stdout.write(merged_ass.dumps())
    sys.stdout.flush()



if __name__ == "__main__":
    assfiles = []
    if len(sys.argv) <= 1:
        usage()
        sys.exit(1)

    sys.argv.pop(0)

    global_options = {}

    globalless_args = []
    i = 0
    while sys.argv:
        param = sys.argv.pop(0)
        if param in ('--global-sync',):
            global_options['sync'] = int(sys.argv.pop(0))
        elif param in ('--add-merge-comments'):
            global_options['add-merge-comments'] = True
        elif param in ('--title'):
            global_options['title'] = sys.argv.pop(0)
        else:
            globalless_args.append(param)

    parameters = []
    local_options = {}
    while globalless_args:
        param = globalless_args.pop(0)
        if param in ('--sync',):
            local_options['sync'] = int(globalless_args.pop(0))
        else:
            # a filename
            options = global_options.copy()
            options.update(local_options)
            parameters.append((options, param))
            local_options = {}

    main(parameters, global_options)


