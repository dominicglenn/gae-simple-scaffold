# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
"""Main application entry point."""

import webapp2
import base
import base.constants
import base.api_fixer
from common import constants
import routes

# These should all inherit from base.handlers.BaseHandler
_UNAUTHENTICATED_ROUTES = routes.public.values()

# These should all inherit from base.handlers.BaseAjaxHandler
_UNAUTHENTICATED_AJAX_ROUTES = routes.api.values()

# These should all inherit from base.handlers.AuthenticatedHandler
_USER_ROUTES = routes.manage.values()

# These should all inherit from base.handlers.AuthenticatedAjaxHandler
_AJAX_ROUTES = []

# These should all inherit from base.handlers.AdminHandler
_ADMIN_ROUTES = []

# These should all inherit from base.handlers.AdminAjaxHandler
_ADMIN_AJAX_ROUTES = []

# These should all inherit from base.handlers.BaseCronHandler
_CRON_ROUTES = routes.cron.values()

# These should all inherit from base.handlers.BaseTaskHandler
_TASK_ROUTES = []

# Place global application configuration settings (e.g. settings for
# 'webapp2_extras.sessions') here.
#
# These values will be accessible from handler methods like this:
# self.app.config.get('foo')
#
# Framework level settings:
#   template: one of base.constants.JINJA2 (default) or base.constants.DJANGO.
#
#   using_angular: True or False (default).  When True, an XSRF-TOKEN cookie
#                  will be set for interception/use by Angular's $http service.
#                  When False, no header will be set (but an XSRF token will
#                  still be available under the _xsrf key for Django/Jinja
#                  templates).  If you set this to True, be especially careful
#                  when mixing Angular and Django/Jinja2 templates:
#                    https://github.com/angular/angular.js/issues/5601
#                  See the summary by IgorMinar for details.
#
#   framing_policy: one of base.constants.DENY (default),
#                   base.constants.SAMEORIGIN, or base.constants.PERMIT
#
#   hsts_policy:    A dictionary with minimally a 'max_age' key, and optionally
#                   a 'includeSubdomains' boolean member.
#                   Default: { 'max_age': 2592000, 'includeSubDomains': True }
#                   implying 30 days of strict HTTPS for all subdomains.
#
#   csp_policy:     A dictionary with keys that correspond to valid CSP
#                   directives, as defined in the W3C CSP 1.1 spec.  Each
#                   key/value pair is transmitted as a distinct
#                   Content-Security-Policy header.
#                   Default: {'default-src': '\'self\''}
#                   which is a very restrictive policy.  An optional
#                   'reportOnly' boolean key substitutes a
#                   'Content-Security-Policy-Report-Only' header
#                   name in lieu of 'Content-Security-Policy' (the default
#                   is base.constants.DEBUG).
#
#  Note that the default values are also configured in app.yaml for files
#  served via the /static/ resources.  You may need to change the settings
#  there as well.

_CONFIG = {
    # Developers are encouraged to build sites that comply with this (or
    # a similarly restrictive) CSP policy.  In particular, adding directives
    # such as unsafe-inline or unsafe-eval is highly discouraged, as these
    # may lead to XSS attacks.

    'csp_policy': {
        # https://developers.google.com/fonts/docs/technical_considerations
        'font-src':    '\'self\' themes.googleusercontent.com *.gstatic.com',
        'frame-src':   '\'self\' *.google.com *.youtube.com *.doubleclick.net https://*.doubleclick.net',

        # NOTE: avoid unsafe-inline
        'script-src':  '\'self\' \'unsafe-inline\' \'unsafe-eval\' data: *.googleapis.com *.ytimg.com *.google.com *.googleanalytics.com *.google-analytics.com *.youtube.com *.googletagmanager.com https://*.googletagmanager.com' ,
        'media-src':  '\'self\' data:',
        'style-src':   '\'self\' \'unsafe-inline\' data: fonts.googleapis.com *.gstatic.com',
        'img-src':     '\'self\' *.gstatic.com *.googleusercontent.com data: *.googleapis.com *.ytimg.com *.withgoogle.com *.google-analytics.com https://*.doubleclick.net',

        # Fallback.
        'default-src': '\'self\' *.gstatic.com *.googleapis.com',
        'report-uri':  '/csp',
        'reportOnly': base.constants.DEBUG,
    },

    'webapp2_extras.i18n': {
        'default_locale': 'en_US'
    },

    'framing_policy': 'SAMEORIGIN',
}

# DEV SERVER ONLY CONFIG
if constants.is_dev_server:
    # Allow BrowserSync server
    _CONFIG['csp_policy']['img-src'] += ' 0.0.0.0:8080'
    _CONFIG['csp_policy']['script-src'] += ' localhost:5001'
    _CONFIG['csp_policy']['connect-src'] = '\'self\' localhost:5001 ws://localhost:5001 *.googleapis.com'

#################################
# DO NOT MODIFY BELOW THIS LINE #
#################################

app = webapp2.WSGIApplication(
    routes=(_UNAUTHENTICATED_ROUTES + _UNAUTHENTICATED_AJAX_ROUTES +
            _USER_ROUTES + _AJAX_ROUTES + _ADMIN_ROUTES + _ADMIN_AJAX_ROUTES +
            _CRON_ROUTES + _TASK_ROUTES),
    debug=base.constants.DEBUG,
    config=_CONFIG)
