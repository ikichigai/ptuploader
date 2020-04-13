#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
from datetime import timedelta
import logging
import requests
import redis
from config import Config as c


def get_redis():
    r = redis.Redis(
        host=c.REDIS_HOST,
        port=c.REDIS_PORT,
        db=1,
        password=c.REDIS_PASSWORD
    )
    return r


def get_token():
    r = get_redis()
    if r.ttl("pttoken") > 1000:
        token = r.get("pttoken")
        logging.info('Got token locally: %s' % token)
    else:
        token = get_token_from_pt()
    return token


def set_token(token, seconds=10000):
    r = get_redis()
    r.setex(
        "pttoken",
        timedelta(seconds=seconds),
        value=token
    )


def get_token_from_pt():
    auth_data = {'client_id': c.PEERTUBE_CLIENT_ID,
                 'client_secret': c.PEERTUBE_CLIENT_SECRET,
                 'grant_type': 'password',
                 'response_type': 'code',
                 'username': c.PEERTUBE_USER,
                 'password': c.PEERTUBE_PASSWORD
                 }

    if c.PEERTUBE_TOKEN == 'access_token':
        try:
            auth_result = requests.post(
                '{0}{1}'.format(c.PEERTUBE_ENDPOINT, '/api/v1/users/token'),
                data=auth_data
                )
            access_token = (auth_result.json()['access_token'])
            expires_in = (auth_result.json()['expires_in'])
            set_token(access_token, expires_in)
            logging.info("Got new token from peertube: %s" % access_token)
        except:
            logging.error("Auth result: %s" % auth_result.text)
            sys.exit(1)
    else:
        access_token = c.PEERTUBE_TOKEN

    set_token(access_token)
    return access_token
