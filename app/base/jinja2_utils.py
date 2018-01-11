import jinja2
from common import user_agent


@jinja2.contextfunction
def user_agent_is_ie(context):
    user_agent_string = context['request'].headers.get('User-Agent', '')

    return user_agent.is_ie(user_agent_string)


@jinja2.contextfunction
def user_agent_is_ie10(context):
    user_agent_string = context['request'].headers.get('User-Agent', '')

    return user_agent.is_ie10(user_agent_string)


@jinja2.contextfunction
def user_agent_supports_http2(context):
    user_agent_string = context['request'].headers.get('User-Agent', '')

    return user_agent.supports_http2(user_agent_string)
