from google.appengine.ext import ndb


class BaseModel(ndb.Model):
    def to_dict(self, include=None, exclude=None):
        result = super(BaseModel, self).to_dict(include=include, exclude=exclude)
        if (not include and not exclude) or (include and 'key' in include) or (exclude and not 'key' in exclude):
            result['key'] = self.key.urlsafe()
        return result

    def copy(self, from_entity, exclude=None, **override_args):
        _class = from_entity.__class__
        props = dict((k, v.__get__(from_entity, _class)) for k, v in _class._properties.iteritems()
                     if type(v) is not ndb.ComputedProperty and k not in exclude)
        props.update(override_args)
        self.populate(**props)
        return self


class BaseQuery(ndb.Query):
    @classmethod
    def from_query(cls, query):
        query.__class__ = cls
        return query

    def _prop(self, name):
        prop = ndb.GenericProperty()
        prop._name = name
        return prop
