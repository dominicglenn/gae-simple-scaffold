# -*- coding: utf-8 -*-

import os
import pytz


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


is_dev_server = 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Development')
locales = ['en-US']

TIMEZONE = pytz.UTC

BASE_PATH = os.path.abspath(
    os.path.dirname(os.path.dirname(__file__))
)


ALLOWED_EMAIL_POSTFIXES = (
)

ALLOWED_EMAILS = (
)

SOCIAL_USER_AGENTS = (
    'facebookexternalhit',
    'LinkedInBot',
    'Google (+https://developers.google.com/+/web/snippet/)',
    'Pinterest',
    'KAKAOSTORY',
    'Twitterbot'
)

