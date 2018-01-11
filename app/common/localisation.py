import re
import hashlib

from google.appengine.ext import ndb
from webapp2_extras import i18n
from babel import Locale


LOCALE_KEY = 'hl'

ngettext = i18n.ngettext


def gettext(text, **variables):
    if not text:
        return None

    hash = hashlib.md5(text).hexdigest()
    translation = i18n.gettext(hash, **variables)
    if translation == hash:
        translation = i18n.gettext(text, **variables)

    return translation


def get_locale():
    return normalise_locale(i18n.get_i18n().locale)


def set_locale(locale=None, handle=None, auto=False, cookie=False):
    if auto:
        locales = sorted(detect_locales(handle).iterkeys(), reverse=True)
        locale = negotiate_locale(locales, handle.locales)
        if not locale:
            locale = i18n.get_store().default_locale

    if locale:
        i18n.get_i18n().set_locale(locale.replace('-', '_'))
        if handle and cookie:
            handle.response.set_cookie(LOCALE_KEY, locale, max_age=15724800)


def negotiate_locale(preferred, available):
    locale = Locale.negotiate(preferred, available, sep='-')

    if locale:
        return normalise_locale(str(locale))

    return None


def normalise_locale(locale):
    if not locale:
        return None

    locale = locale.replace('_ALL', '').replace('ALL_', '').replace('_', '-')
    parts = locale.split('-')

    if len(parts) == 1:
        return parts[0].lower()

    if len(parts) == 2:
        return parts[0].lower() + '-' + parts[1].upper()

    return None


def normalise_locales(locales):
    if not locales:
        return None

    if isinstance(locales, dict):
        return {normalise_locale(lc): q for lc, q in locales.iteritems()}

    if isinstance(locales, list):
        return [normalise_locale(lc) for lc in locales]

    return None


def detect_locales(handle):
    # locale from query string
    locale = normalise_locale(handle.request.get(LOCALE_KEY, None))
    if locale:
        return {locale: 1}

    # locale from cookie
    locale = normalise_locale(handle.request.cookies.get(LOCALE_KEY, None))
    if locale:
        return {locale: 1}

    # locale from accept language header
    locales = normalise_locales(accept_header_locales(handle))
    if locales:
        return locales

    # default locale
    locale = i18n.get_store().default_locale
    return {locale: 1}


def accept_header_locales(handle, pattern='([a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?)\s*(;\s*q\s*=\s*(1|0\.[0-9]+))?'):
    # https://github.com/mikeolteanu/livepythonconsole-app-engine/blob/master/boilerplate/lib/i18n.py

    accept_language = handle.request.headers.get('Accept-Language', None)

    if not accept_language:
        return None

    locales = {}

    for match in re.finditer(pattern, accept_language):
        if None == match.group(4):
            quality = 1
        else:
            quality = match.group(4)

        locale = match.group(1).replace('_', '-')

        if len(locale) == 2:
            locale = locale.lower()
        elif len(locale) == 5:
            locale = locale.split('-')[0].lower() + '-' + locale.split('-')[1].upper()
        else:
            locale = None

        if locale:
            locales[locale] = float(quality)

    return locales


def get_display_name(for_locale, in_locale=None):
    for_locale = normalise_locale(for_locale)

    if in_locale:
        in_locale = normalise_locale(in_locale)
    else:
        in_locale = for_locale

    return Locale.parse(for_locale, sep='-').get_display_name(in_locale.replace('-', '_'))


class TranslatedProperty(ndb.StringProperty):

    def _get_value(self, entity):
        return gettext(super(TranslatedProperty, self)._get_value(entity))
