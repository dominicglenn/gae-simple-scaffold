import re


PRIORITY_HTTP2_USER_AGENTS = (
    # Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)
    # Internet Explorer - 11+
    ('MSIE', re.compile(r'^.*MSIE\s([\d.]+).*$'), lambda x: x >= 11),

    # Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10136
    # Edge - 12 +
    ('Edge', re.compile(r'^.*Edge/([\d.]+).*$'), lambda x: x >= 12),

    # Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36 OPR/15.0.1147.100
    # Opera - 28+
    ('OPR', re.compile(r'^.*OPR/([\d.]+).*$'), lambda x: x >= 28),

    # Mozilla/5.0 (Macintosh; PPC Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0
    # Firefox & Firefox Android - 36+
    ('Firefox', re.compile(r'^.*Firefox/([\d.]+).*$'), lambda x: x >= 36),
)

OPTIONAL_HTTP2_USER_AGENTS = (
    # Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19
    # Chrome & Chrome Android - 41+
    ('Chrome', re.compile(r'^.*Chrome/([\d.]+).*$'), lambda x: x >= 41),

    # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7
    # Safari & iOS Safari - 9+
    ('Safari', re.compile(r'^.*Version/([\d.]+) Safari/.*$'), lambda x: x >= 9),
)


IE_10_REGEX = re.compile(r'^.*MSIE\s([\d.]+).*$')


def is_ie10(user_agent_string):
    match = IE_10_REGEX.match(user_agent_string)

    if match is not None:
        (value,) = match.groups()

        if value == '10.0':
            return True

    return False


def is_ie(user_agent_string):
    return 'MSIE' in user_agent_string or 'Trident/' in user_agent_string


def supports_http2(user_agent_string):
    for browser, regex, match_func in PRIORITY_HTTP2_USER_AGENTS:
        if browser in user_agent_string:
            match = regex.match(user_agent_string)

            value = _get_version_number_from_match(match)

            if value is not None and match_func(value):
                return True

            else:
                return False

    for browser, regex, match_func in OPTIONAL_HTTP2_USER_AGENTS:
        match = regex.match(user_agent_string)

        value = _get_version_number_from_match(match)

        if value is not None and match_func(value):
            return True

    return False


def _get_version_number_from_match(match):
    try:
        (value,) = match.groups()
        value = '.'.join(value.split('.')[:2])
        value = float(value)

    except (AttributeError, ValueError):
        value = None

    return value
