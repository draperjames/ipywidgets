# encoding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""
Trait types for html widgets.
"""

import re
import datetime as dt
from .eventful import Eventful
from .traitlets_patch import FrozenBunch as Bunch
from traitlets import (Undefined, Dict, Instance, Unicode, TraitType, List,
                       TraitError)


_color_names = ['aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'honeydew', 'hotpink', 'indianred ', 'indigo ', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightsteelblue', 'lightyellow', 'lime', 'limegreen', 'linen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'rebeccapurple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'white', 'whitesmoke', 'yellow', 'yellowgreen']

_color_re = re.compile(r'#[a-fA-F0-9]{3}(?:[a-fA-F0-9]{3})?$')


class Color(Unicode):
    """A string holding a valid HTML color such as 'blue', '#060482', '#A80'"""

    info_text = 'a valid HTML color'
    default_value = Undefined

    def validate(self, obj, value):
        if value.lower() in _color_names or _color_re.match(value):
            return value
        self.error(obj, value)


class Datetime(TraitType):
    """A trait type holding a Python datetime object"""

    klass = dt.datetime
    default_value = dt.datetime(1900, 1, 1)


class Date(TraitType):
    """A trait type holding a Python date object"""

    klass = dt.date
    default_value = dt.date(1900, 1, 1)


def datetime_to_json(pydt, manager):
    """Serialize a Python datetime object to json.

    Instantiating a JavaScript Date object with a string assumes that the
    string is a UTC string, while instantiating it with constructor arguments
    assumes that it's in local time:

    >>> cdate = new Date('2015-05-12')
    Mon May 11 2015 20:00:00 GMT-0400 (Eastern Daylight Time)
    >>> cdate = new Date(2015, 4, 12) // Months are 0-based indices in JS
    Tue May 12 2015 00:00:00 GMT-0400 (Eastern Daylight Time)

    Attributes of this dictionary are to be passed to the JavaScript Date
    constructor.
    """
    if pydt is None:
        return None
    else:
        return dict(
            year=pydt.year,
            month=pydt.month - 1,  # Months are 0-based indices in JS
            date=pydt.day,
            hours=pydt.hour,       # Hours, Minutes, Seconds and Milliseconds
            minutes=pydt.minute,   # are plural in JS
            seconds=pydt.second,
            milliseconds=pydt.microsecond / 1000
        )


def datetime_from_json(js, manager):
    """Deserialize a Python datetime object from json."""
    if js is None:
        return None
    else:
        return dt.datetime(
            js['year'],
            js['month'] + 1,  # Months are 1-based in Python
            js['date'],
            js['hours'],
            js['minutes'],
            js['seconds'],
            js['milliseconds'] * 1000
        )

datetime_serialization = {
    'from_json': datetime_from_json,
    'to_json': datetime_to_json
}


class InstanceDict(Instance):
    """An instance trait which coerces a dict to an instance.

    This lets the instance be specified as a dict, which is used
    to initialize the instance.

    Also, we default to a trivial instance, even if args and kwargs
    is not specified."""

    def validate(self, obj, value):
        if isinstance(value, dict):
            return super(InstanceDict, self).validate(obj, self.klass(**value))
        else:
            return super(InstanceDict, self).validate(obj, value)

    def make_dynamic_default(self):
        return self.klass(*(self.default_args or ()),
                          **(self.default_kwargs or {}))


# The regexp is taken
# from https://github.com/d3/d3-format/blob/master/src/formatSpecifier.js
_number_format_re = re.compile('^(?:(.)?([<>=^]))?([+\-\( ])?([$#])?(0)?(\d+)?(,)?(\.\d+)?([a-z%])?$', re.I)

# The valid types are taken from
# https://github.com/d3/d3-format/blob/master/src/formatTypes.js
_number_format_types = {
    'e', 'f', 'g', 'r', 's', '%', 'p', 'b', 'o', 'd', 'x',
    'X', 'c', ''
}


class NumberFormat(Unicode):
    """A string holding a number format specifier, e.g. '.3f'

    This traitlet holds a string that can be passed to the
    `d3-format <https://github.com/d3/d3-format>`_ JavaScript library.
    The format allowed is similar to the Python format specifier (PEP 3101).
    """

    info_text = 'a valid number format'
    default_value = Undefined

    def validate(self, obj, value):
        value = super(NumberFormat, self).validate(obj, value)
        re_match = _number_format_re.match(value)
        if re_match is None:
            self.error(obj, value)
        else:
            format_type = re_match.group(9)
            if format_type is None:
                return value
            elif format_type in _number_format_types:
                return value
            else:
                raise TraitError(
                    'The type specifier of a NumberFormat trait must '
                    'be one of {}, but a value of \'{}\' was '
                    'specified.'.format(
                        list(_number_format_types), format_type)
                )


class EventfulElements(Eventful):

    event_map = {
        "setitem": "__setitem__",
        "delitem": "__delitem__",
    }

    @staticmethod
    def _before_setitem(value, call):
        key = call.args[0]
        try:
            old = value[key]
        except (KeyError, IndexError):
            old = Undefined
        return key, old

    @staticmethod
    def _after_setitem(value, answer):
        key, old = answer.before
        new = value[key]
        if new != old:
            return Bunch(key=key, old=old, new=new)

    @staticmethod
    def _before_delitem(value, call):
        key = call.args[0]
        try:
            old = value[key]
        except KeyError:
            pass
        else:
            return Bunch(key=key, old=old)


class EventfulDict(EventfulElements, Dict):

    klass = dict
    type_name = 'edict'
    event_map = {
        'setitem': ('__setitem__', 'setdefault'),
        'delitem': ('__delitem__', 'pop'),
        'update': 'update',
        'clear': 'clear',
    }

    def _before_update(self, value, call):
        if len(call.args):
            new = call.args[0]
            new.update(call.kwargs)
        else:
            new = call.kwargs
        with self.abstracted(value, "setitem") as setitem:
            for k, v in new.items():
                setitem(k, v)
        return setitem

    def _before_clear(self, value, call):
        with self.abstracted(value, "delitem") as delitem:
            for k in value.keys():
                delitem(k)
        return delitem


class EventfulList(EventfulElements, List):

    event_map = {
        'append': 'append',
        'extend': 'extend',
        'setitem': '__setitem__',
        'remove': "remove",
        'delitem': '__delitem__',
        'reverse': 'reverse',
        'sort': 'sort',
    }
    type_name = 'elist'

    def _before_append(self, value, call):
        with self.abstracted_once(value, "setitem") as setitem:
            setitem(len(value), call.args[0])
        return setitem

    def _before_extend(self, value, call):
        with self.abstracted(value, "setitem") as setitem:
            for i, v in enumerate(call.args[0]):
                setitem(i, v)
        return setitem

    def _before_remove(self, value, call):
        with self.abstracted_once(value, "delitem") as delitem:
            delitem(value.index(call.args[0]))
        return delitem

    def _before_reverse(self, value, call):
        return self.rearrangement(value)

    def _before_sort(self, value, call):
        return self.rearrangement(value)

    @staticmethod
    def rearrangement(new):
        old = new[:]
        def after_rearangement(value):
            return Bunch(old=old, new=new)
        return after_rearangement
