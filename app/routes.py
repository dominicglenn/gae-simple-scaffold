import collections

from webapp2_extras.routes import RedirectRoute as Route

from common import route_utils
from handlers import index


public = collections.OrderedDict([
    ('index', Route('/<path:(?!(api|share|cron|manage)).*>', index.IndexHandler)),
])

cron = {
}

api = collections.OrderedDict([
])

manage = collections.OrderedDict([
])

route_utils.prepare([
    ('manage', manage),
    ('public', public),
    ('api', api),
    ('cron', cron),
])
