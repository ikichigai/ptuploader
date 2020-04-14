#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from mimetypes import guess_type
import requests
from tokenstore import get_token
from config import Config as c


logging.basicConfig(
    filename=c.LOG_FILE_PATH,
    format=u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.INFO
    )

videodir = sys.argv[1]

for videofile in os.listdir(videodir):
    if videofile.endswith(".mp4"):
        file_path = os.path.join(videodir, videofile)
        file_name = os.path.basename(file_path)
        file_mime_type = guess_type(file_path)[0]
        logging.info("Accept file for uploading: %s" % file_name)

        channelId = requests.get(
            '{0}{1}/{2}'.format(c.PEERTUBE_ENDPOINT, '/api/v1/video-channels', c.PEERTUBE_CHANNEL)
            ).json()['id']

        upload_data = {'channelId': channelId,
                       'privacy': '2',
                       'commentsEnabled': True,
                       'name': file_name
                       }

        access_token = get_token()
        upload_headers = {'Authorization': 'Bearer {0}'.format(access_token)}

        with open(file_path, 'rb') as f:
            upload_result = requests.post(
                '{0}{1}'.format(c.PEERTUBE_ENDPOINT, '/api/v1/videos/upload'),
                headers=upload_headers,
                data=upload_data,
                files={"videofile": (file_name, f, file_mime_type)}
                )
            try:
                video_uuid = upload_result.json()['video']['uuid']
                logging.info("%s%s/%s" % (c.PEERTUBE_ENDPOINT, '/videos/watch', video_uuid))
            except:
                logging.info("Upload result: %s" % upload_result.text)
                sys.exit(1)
