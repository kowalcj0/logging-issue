# -*- coding: utf-8 -*-
import os
import logging

import requests
from behave import *  # noqa


def before_all(context):
    context.platform_url = 'http://jsonplaceholder.typicode.com'

    # configure logger
    fmt = '%(asctime)s-%(filename)s[line:%(lineno)d]-%(name)s-%(levelname)s: %(message)s'
    context.config.setup_logging(level=logging.DEBUG,
                                 format=fmt,
                                 filename='./reports/behave.log',
                                 filemode='a'
                                 )

    # Check if platform is up
    try:
        requests.get(context.platform_url)
    except requests.ConnectionError:
        raise Exception("Unable to connect to platform URL {} - please ensure "
                        "the platform is running correctly"
                        .format(context.platform_url))
