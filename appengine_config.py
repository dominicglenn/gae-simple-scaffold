from __future__ import absolute_import

import os

from google.appengine.ext import vendor


DEBUG = os.environ.get('SERVER_SOFTWARE', '').startswith('Development')

BASE_DIR = os.path.dirname(__file__)
SITE_PACKAGES = os.path.join(BASE_DIR, 'site-packages')

vendor.add(os.path.join('app'))

if DEBUG:
    vendor.add(os.path.join(SITE_PACKAGES, 'dev'))

vendor.add(os.path.join(SITE_PACKAGES, 'prod'))
