import functools
import json

from google.appengine.api import users
from webapp2_extras import sessions

import handlers
import xsrf
from common import constants, utility
from base.constants import DEFAULT_ANGULAR


SESSION_USER_IS_LOGGED_IN = 'user_is_logged_in'


def email_is_valid(email):
    for postfix in constants.ALLOWED_EMAIL_POSTFIXES:
        if email.endswith(postfix):
            return True

    for email_ in constants.ALLOWED_EMAILS:
        if email.strip().lower() == email_.strip().lower():
            return True

    return False


def user_is_allowed(user):
    if constants.is_dev_server:
        return True

    elif not user:
        return False

    elif not email_is_valid(user.email()):
        return False

    return True


def session_has_valid_password(request):
    session_store = sessions.get_store(request=request)
    session = session_store.get_session()

    return session.get(SESSION_USER_IS_LOGGED_IN, False)


def save_login_state_to_session(request, response, is_logged_in):
    session_store = sessions.get_store(request=request)
    session = session_store.get_session()

    session[SESSION_USER_IS_LOGGED_IN] = is_logged_in
    session_store.save_sessions(response)

    return response


def requires_auth(f):
    """A decorator that requires a currently logged in user."""
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        current_user = users.get_current_user()

        is_cron_request = self.request.headers.get('X-AppEngine-Cron', 'false')
        is_cron_request = is_cron_request == 'true'

        if users.is_current_user_admin():
            return f(self, *args, **kwargs)

        elif is_cron_request:
            return f(self, *args, **kwargs)

        elif user_is_allowed(current_user):
            return f(self, *args, **kwargs)

        else:
            self.DenyAccess()

    return wrapper


class AjaxHandlerMixin(object):
    def _SetAjaxResponseHeaders(self):
        self.response.headers['Content-Disposition'] = 'attachment; filename=json'
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'

    def render_json(self, obj):
        self._SetAjaxResponseHeaders()
        self._RawWrite(json.dumps(obj, default=utility.json_default))


class XSRFTokenValidationMixin(object):
    def get_xsrf_token(self):
        return handlers._GetXsrfKey()

    def _RequestContainsValidXsrfToken(self):
        token = self.request.get('xsrf') or self.request.headers.get('X-XSRF-TOKEN')
        # By default, Angular's $http service will add quotes around the
        # X-XSRF-TOKEN.
        if (token and
                self.app.config.get('using_angular', DEFAULT_ANGULAR) and
                    token[0] == '"' and token[-1] == '"'):
            token = token[1:-1]

        current_email = self.current_user.email() if self.current_user is not None else ''
        if xsrf.ValidateToken(self.get_xsrf_token(), current_email, token):
            return True
        return False

    def XsrfFail(self):
        self.abort(401)


class AuthenticatedHandler(handlers.BaseHandler, XSRFTokenValidationMixin):
    @requires_auth
    @handlers.xsrf_protected
    def dispatch(self):
        super(AuthenticatedHandler, self).dispatch()

    __metaclass__ = handlers._HandlerMeta

    def DenyAccess(self):
        user = users.get_current_user()

        context = {
            'login_url': users.create_login_url(self.request.url),
            'user_email': user.email() if user else None
        }

        self.render('unauthenticated.html', context)
