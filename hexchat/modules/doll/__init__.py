
from itertools import zip_longest
import functools
import inspect

from .validators import Numeric, Optional, ValidationError, PassException

import hexchat


def ucc_to_lower(text, separator='_'):
    """UpperCamelCase to upper_camel_case"""
    output = text[0].lower()
    for char in text[1:]:
        if char == char.upper():
            output += separator + char.lower()
        else:
            output += char.lower()
    return output


def setup_command(prefix='!', separator='-'):
    """Generate a new class with base `Command`"""
    return type(
        'CommandBase',
        (Command,),
        dict(_prefix=prefix, _separator=separator))


class Command:

    _prefix = None
    _separator = None

    def __new__(cls, *args, **kwargs):
        # generate command name
        cls._command_name = ucc_to_lower(cls.__name__, cls._separator)
        cls._command = cls._prefix + cls._command_name
        obj = super().__new__(cls)

        obj._error_handler = None
        obj._fields = []
        for key, field in cls.__dict__.items():
            if not key.startswith('_'):
                if isinstance(field, Field):
                    obj.add_field((key, field))

        return obj

    def add_field(self, field):
        self._fields.append(field)

    def _callback(self, word, word_eol, userdata):

        text = word_eol[3][1:]
        words = text.split()
        if not words or words[0].lower() != self._command:
            return

        args = words[1:]
        success = True
        values = []

        # take the values from IRC, validate and convert them
        for value, (name, field) \
                in zip_longest(args, self._fields, fillvalue=""):
            try:
                field.validate(value)
                values.append(field.convert(value))
            except PassException as e:
                values.append(None)
            except ValidationError as e:
                success = False
                if self._error_handler is not None:
                    self._error_handler(e)
                    return
                else:
                    raise
            except ConversionError as e:
                success = False
                if self._error_handler is not None:
                    self._error_handler(e)
                    return
                else:
                    raise

        if success:
            return self._func(*values, userdata=userdata)

    def __call__(self, func):
        self._func = func
        self._func_args = inspect.getargspec(func)

        arg_set = set(self._func_args.args)

        # check if function signature matches fields
        for name, field in self._fields:
            if name in arg_set:
                arg_set.remove(name)
            else:
                raise TypeError(
                    "Argument {!r} not in signature of function {!r}".format(
                        name, self._func))

        # the order of the function signature determines the orden, in
        # which the arguments are expected from the IRC command
        sort_dict = {v: i for i, v in enumerate(self._func_args.args)}
        self._fields.sort(key=lambda e: sort_dict[e[0]])

        self._hook = hexchat.hook_server('PRIVMSG', self._callback)
        return func

    def error_handler(self, func):
        self._error_handler = func
        return func


# Field and types

class ConversionError(Exception):
    pass


class Field:

    def __init__(self, _type, validators=None):
        if validators is None:
            validators = []

        if isinstance(_type, type):
            _type = _type()
        self._type = _type
        self.validators = list(validators)
        self.validators.extend(list(_type.validators))

    def validate(self, value):
        for validator in self.validators:
            if isinstance(validator, type):
                validator = validator()
            validator.validate(value)

    def convert(self, value):
        return self._type.convert(value)


class BaseType:
    validators = None

    def __new__(cls, *args, **kwargs):
        if cls.validators is None:
            cls.validators = []
        return super().__new__(cls)

    def convert(self, value):
        raise NotImplementedError("convert is not implented.")


class Integer(BaseType):
    validators = [Numeric]

    def convert(self, value):
        return int(value)
