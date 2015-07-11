import logging

from behave import *  # noqa

from .Client import Client


def make_request(context, method):
    if hasattr(context, "post_body"):
        if context.post_body is not None:
            data = context.post_body
    else:
        data=None

    context.response = context.client.request(
        method=method,
        path=context.resource_url,
        payload=data,
    )


@given(u'a http client')
def step_impl(context):
    client = Client(platform_url=context.platform_url)
    client.set_content_type_as_json()
    client.set_accept_type_as_json()
    context.client = client


@when(u'I make {VERB} request')
def step_impl(context, VERB):
    make_request(context, VERB)


@when(u'I access resource "{resource_url}"')
def step_impl(context, resource_url):
    context.resource_url = resource_url


@then(u'the status code should be "{status_code}"')
def step_impl(context, status_code):
    assert int(status_code) == context.response.status_code, (
            u"Expected: {} but got: {}".format(status_code,
                context.response.status_code))
