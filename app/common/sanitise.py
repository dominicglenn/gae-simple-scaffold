import csv
import cgi
import re
import imghdr

from google.appengine.ext import ndb
from django.utils.html import strip_tags as django_strip_tags
from django.utils.html import conditional_escape as django_conditional_escape
from django.utils.http import urlquote as django_urlquote
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from utility import clamp


def parse_str(_str, default=None, whitelist=None, strip_tags=False, entities=False, url_quote=False):
    if _str is None:
        return default

    _str = unicode(_str)

    if whitelist and _str not in whitelist:
        return default

    if strip_tags:
        _str = django_strip_tags(_str)

    if entities:
        _str = django_conditional_escape(_str)

    if url_quote:
        _str = django_urlquote(_str)

    return _str


def parse_url(url, default=None, schemes=list(['http', 'https'])):
    # validate scheme manually (as option was not implemented on django 1.5)
    if not re.match('^(' + '|'.join(schemes) + ')', url):
        return default

    # use django validator
    validate = URLValidator()

    try:
        validate(url)
    except ValidationError:
        return default

    # if no ValidationError then url is valid
    return url


def parse_int(_int, default=None, clamp_min=None, clamp_max=None, whitelist=None, base=10):
    if isinstance(_int, int):
        parsed_int = _int
    else:
        try:
            parsed_int = int(_int, base)
        except (ValueError, TypeError):
            parsed_int = default

    if whitelist and parsed_int not in whitelist:
        return default

    return clamp(parsed_int, clamp_min, clamp_max)


def parse_bool(_bool, default=None):
    if isinstance(_bool, bool):
        parsed_bool = _bool
    else:
        _bool = str(_bool).strip().lower()

        if _bool in ['true', '1']:
            parsed_bool = True
        elif _bool in ['false', '0']:
            parsed_bool = False
        else:
            parsed_bool = default

    return parsed_bool


def parse_list(_list, default=None, cast=None):
    if isinstance(_list, list):
        parsed_list = _list
    else:
        if not _list:
            return default

        parsed_list = []
        for fields in csv.reader([_list]):
            for i, field in enumerate(fields):
                parsed_list.append(field)

    if cast:
        parsed_list = [cast(x) for x in parsed_list]

    return parsed_list


def parse_key(key, kind=None, default=None):
    # https://code.google.com/p/appengine-ndb-experiment/issues/detail?id=143
    if isinstance(key, ndb.Key):
        parsed_key = key
    else:
        try:
            parsed_key = ndb.Key(urlsafe=key)
        except Exception, e:
            if e.__class__.__name__ == 'ProtocolBufferDecodeError':
                return default
            else:
                raise

    if kind and parsed_key.kind() != kind._get_kind():
        return default

    return parsed_key


def parse_file(field_storage, default=None, whitelist=None, max_size=None):
    if not isinstance(field_storage, cgi.FieldStorage):
        return default

    if whitelist:
        mime_type = field_storage.type.lower()

        if not mime_type in whitelist:
            return default

        # if image file, do a deeper check
        if mime_type.startswith('image'):
            detected_type = 'image/' + imghdr.what(None, field_storage.file.getvalue())
            if mime_type != detected_type:
                return default

    if max_size:
        field_storage.file.seek(0, 2)
        size = field_storage.file.tell()
        field_storage.file.seek(0)
        if size > max_size:
            return default

    return field_storage
