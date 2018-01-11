import collections
import datetime
import re
import random
import string

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from base import api_fixer


def request(url, payload=None, deadline=15, no_cache=True, **kwargs):
    # prevent appengine caching - https://aralbalkan.com/1510/
    if no_cache:
        headers = kwargs.get('headers', {})
        headers.update({'Cache-Control': 'no-cache,max-age=0', 'Pragma': 'no-cache'})
    else:
        headers = None

    return urlfetch.fetch(
        url,
        payload=payload,
        headers=headers,
        deadline=deadline,
        validate_certificate=True,
        **kwargs
    )


def chunks(items, max_size):
    """
    http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(items), max_size):
        yield items[i:i + max_size]


def keys_only(item):
    if isinstance(item, ndb.Key):
        return item

    if hasattr(item, 'key'):
        return item.key

    if isinstance(item, collections.Iterable):
        return map(lambda x: keys_only(x), item)

    return None


def entities_to_dict(entities, get=None, **kwargs):
    if entities is None:
        return None

    is_iterable = isinstance(entities, collections.Iterable)

    if not is_iterable:
        entities = [entities]

    entity_dicts = [None if not entity else entity.to_dict(**kwargs) for entity in entities]

    if get:
        for entity_dict in entity_dicts:
            if entity_dict:
                resolve_entity_dict(entity_dict, get)

    return entity_dicts if is_iterable else entity_dicts[0]


def resolve_entity_dict(entity_dict, props):
    for prop in props:
        values = entity_dict[prop]
        if not isinstance(values, collections.Iterable):
            if values and callable(getattr(values, 'get')):
                entity_dict[prop] = values.get()
        else:
            entity_dict[prop] = ndb.get_multi(values)


def clamp(x, _min=None, _max=None):
    if _min is not None and _max is not None:
        return max(min(x, _max), _min)

    if _min is not None:
        return max(x, _min)

    if _max is not None:
        return min(x, _max)

    return x


def json_default(obj):
    if isinstance(obj, ndb.Key):
        return {'key': obj.urlsafe()}

    if isinstance(obj, datetime.datetime):
        return obj.isoformat()


def url_name(name):
    return re.sub(r'^\-|\-$', '', re.sub(r'\W+', '-', name)).lower()


def try_key_get(key, kind=None, default=None):
    from sanitise import parse_key
    key = parse_key(key, kind)
    if key:
        return key.get()
    return default


def rand_str(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))
