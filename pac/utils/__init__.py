# -*- coding: utf-8 -*-

"""
    Borrowed from tipfy (http://tipfy.org) by moraes
"""

import re
import unicodedata

def _unicode(value):
    """Encodes a string value to unicode if not yet decoded.

    :param value:
        Value to be decoded.
    :returns:
        A decoded string.
    """
    if isinstance(value, str):
        return value.decode("utf-8")

    assert isinstance(value, unicode)
    return value

def slugify(value, max_length=None, default=None):
    """Converts a string to slug format (all lowercase, words separated by
    dashes).

    :param value:
        The string to be slugified.
    :param max_length:
        An integer to restrict the resulting string to a maximum length.
        Words are not broken when restricting length.
    :param default:
        A default value in case the resulting string is empty.
    :returns:
        A slugified string.
    """
    value = _unicode(value)
    s = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').lower()
    s = re.sub('-+', '-', re.sub('[^a-zA-Z0-9-]+', '-', s)).strip('-')
    if not s:
        return default

    if max_length:
        # Restrict length without breaking words.
        while len(s) > max_length:
            if s.find('-') == -1:
                s = s[:max_length]
            else:
                s = s.rsplit('-', 1)[0]

    return s

  