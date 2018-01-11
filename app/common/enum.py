#
#  http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
#


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    by_value = dict((value, key) for key, value in enums.iteritems())
    by_key = dict((key, value) for key, value in enums.iteritems())
    enums['keys'] = by_value.keys()
    enums['values'] = by_key.values()
    enums['by_value'] = by_value
    enums['by_key'] = by_key
    return type('Enum', (), enums)

