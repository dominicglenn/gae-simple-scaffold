

def prepare(pairs):
    for pair in pairs:
        for name, route in pair[1].iteritems():
            route.name = pair[0] + '.' + name
            route.strict_slash = True
