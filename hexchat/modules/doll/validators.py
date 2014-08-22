#!/usr/bin/env python3

import re


class ValidationError(Exception):
    pass


class PassException(Exception):
    pass


class BaseValidator:

    def validate(self, value):
        raise NotImplementedError("validate is not implemented")


class Numeric(BaseValidator):

    _pattern = re.compile(r'^\d+$')

    def validate(self, value):
        m = self._pattern.match(value)
        if m is None:
            raise ValidationError("value is not a number.")


class Optional(BaseValidator):

    def validate(self, value):
        if value == "":
            raise PassException()
