
import re
import string
import inspect
import datetime


import hexchat


class ConversionError(Exception):
    pass


class ValidationError(Exception):
    pass


def slug_command(text):
    output = text[0].lower()
    for char in text[1:]:
        if char == char.upper():
            output += '-' + char.lower()
        else:
            output += char.lower()
    output = re.sub(r'[^a-z0-9]+', '-', output).strip('-')
    return output


def prefixed(prefix):
    return Command(prefix)


class Command:

    def __init__(self, prefix):
        self._prefix = prefix
        self._commands = {}

    def _get_handle_mapping(self, cmd_name):
        cmd = self._prefix + cmd_name

        if cmd not in self._commands:
            self._commands[cmd] = {
                'func': None,
                'error_handler': None,
                'func_args': None,
            }
        return self._commands[cmd]

    def _callback(self, word, word_eol, userdata):
        text = word_eol[3][1:]
        words = text.split()
        if not words:
            return

        for command, handlers in self._commands.items():
            if words[0].lower() == command:
                try:
                    self._handle_command(words[1:], handlers)
                except ValidationError as exception:
                    if handlers['error_handler'] is not None:
                        handlers['error_handler'](exception)
                except ConversionError as exception:
                    if handlers['error_handler'] is not None:
                        handlers['error_handler'](exception)

    def _handle_command(self, args, handlers):
        """Handle one command. get the specified arguments,
        validate and convert them"""
        func = handlers['func']
        func_args = handlers['func_args'].args
        func_defaults = handlers['func_args'].defaults

        if func_args is None:
            func_args = []

        if func_defaults is None:
            func_defaults = []

        minimum, maximum = \
            len(func_args) - len(func_defaults), len(func_args)

        if minimum <= len(args) <= maximum:
            annotations = handlers['func_args'].annotations

            final_arguments = []
            failed = False

            for field, value in zip(func_args, args):
                if field in annotations:
                    converter = annotations[field]
                    if isinstance(converter, type):
                        converter = converter()

                    try:
                        value = converter.convert(
                            value, *converter.args, **converter.kwargs)
                    except Exception as e:
                        raise ConversionError(e)

                final_arguments.append(value)
            func(*final_arguments)
        else:
            raise ValidationError(
                'got {} arguments expected {}'.format(
                    len(args),
                    minimum if minimum == maximum else '{}-{}'
                    .format(minimum, maximum)))

    def __call__(self, func):
        cmd = self._get_handle_mapping(slug_command(func.__name__))
        cmd['func'] = func
        cmd['func_args'] = inspect.getfullargspec(func)
        hexchat.hook_server('PRIVMSG', self._callback)
        return func

    def error_handler(self, func):
        cmd = self._get_handle_mapping(slug_command(func.__name__))
        cmd['error_handler'] = func
        return func


class BaseType:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def convert(self, value, *args, **kwargs):
        return value


class Integer(BaseType):

    def convert(self, value):
        return int(value)


class String(BaseType):
    def convert(self, value, minlen=None, maxlen=None):
        if minlen is not None:
            if len(value) < minlen:
                raise ValueError('{!r} is too short.'.format(value))
        if maxlen is not None:
            if len(value) > maxlen:
                raise ValueError('{!r} is too long.'.format(value))
        return value


class Date(BaseType):
    def convert(self, value, date_format=None):
        if date_format is None:
            date_format = r'^(?P<year>(?:\d{2}|\d{4}))-'\
                '(?P<month>\d{1,2})-(?P<day>\d{1,2})$'
        if isinstance(date_format, str):
            date_format = re.compile(date_format)

        m = date_format.match(value)
        if m is None:
            raise ValueError('{!r} is not a valid date.'.format(value))

        return datetime.date(
            int(m.group('year')),
            int(m.group('month')),
            int(m.group('day'))
        )


class Time(BaseType):
    def convert(self, value, time_format=None):

        if not value:
            raise ValueError('Time is missing.')

        if time_format is None:
            time_format = \
                r'^'\
                '(?:(?P<hour>\d+))?'\
                '(?::(?P<minute>\d{1,2}))?'\
                '(?::(?P<second>\d{1,2}))?'\
                '(?:.(?P<micro_second>\d{1,6}))?'\
                '$'
        if isinstance(time_format, str):
            time_format = re.compile(time_format)

        m = time_format.match(value)
        if m is None:
            raise ValueError('{!r} is not a valid time.'.format(value))

        hour = int(m.group('hour')) \
            if m.group('hour') is not None else 0
        minute = int(m.group('minute')) \
            if m.group('minute') is not None else 0
        second = int(m.group('second')) \
            if m.group('second') is not None else 0
        micro_second = int(m.group('micro_second')) \
            if m.group('micro_second') is not None else 0

        return datetime.time(hour, minute, second, micro_second)
