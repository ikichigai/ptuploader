#!/usr/bin/python3
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
        decode_responses=True,
        password=c.REDIS_PASSWORD
    )
    return r


def get_token():
    r = get_redis()
    if r.ttl("pttoken") > 1000:
        token = str(r.get("pttoken"))
        logging.info("Got token locally: %s" % token)
    else:
        token = get_token_from_pt()
    return token


def set_token(token):
    r = get_redis()
    r.delete("pttoken")
    try:
        r.setex(
            "pttoken",
            timedelta(seconds=80000),
            # not works with python2
            "{0}".format(token)
        )
    except Exception as e:
        logging.error("Cannot pass token to uploader: %s", e.message)


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
            access_token = auth_result.json()['access_token']
            logging.info("Got new token from peertube: %s" % access_token)
        except Exception as e:
            logging.error("Error: %s, Auth result: %s" % (e.message, auth_result.text))
            sys.exit(1)
    else:
        access_token = c.PEERTUBE_TOKEN

    print(access_token)
    set_token(str(access_token))
    return access_token
