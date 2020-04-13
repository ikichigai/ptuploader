#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import requests
import logging
from config import LOG_FILE_PATH, PEERTUBE_CHANNEL, PEERTUBE_CLIENT_ID, \
        PEERTUBE_CLIENT_SECRET, PEERTUBE_TOKEN, PEERTUBE_ENDPOINT, JIBRI_RECORDS_PATH
from mimetypes import guess_type


logging.basicConfig(
        filename = LOG_FILE_PATH,
        format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
        level = logging.INFO
        )

videodir = sys.argv[1]

for videofile in os.listdir(videodir):
    if videofile.endswith(".mp4"):
        file_path = os.path.join(videodir, videofile)
        file_name = os.path.basename(file_path)
        file_mime_type = guess_type(file_path)[0]
        logging.info( '{0}{1}'.format(u'Accept file for uploading: ', file_name) )

        channelId = requests.get(
            '{0}{1}/{2}'.format(PEERTUBE_ENDPOINT,'/api/v1/video-channels', PEERTUBE_CHANNEL)
            ).json()['id']

        auth_data = {'client_id': PEERTUBE_CLIENT_ID,
                     'client_secret': PEERTUBE_CLIENT_SECRET,
                     'grant_type': 'password',
                     'response_type': 'code',
                     'username': None,
                     'password': None
                     }

        upload_data = {'channelId': channelId,
                       'privacy': '2',
                       'commentsEnabled': True,
                       'name': file_name
                       }

        upload_headers = {'Authorization': 'Bearer {0}'.format(PEERTUBE_TOKEN)}

        with open(file_path, 'rb') as f:
            upload_result = requests.post('{0}{1}'.format(PEERTUBE_ENDPOINT, '/api/v1/videos/upload'),
                                          headers=upload_headers,
                                          data=upload_data,
                                          files={"videofile": (file_name, f, file_mime_type)})
            try:
                video_uuid = upload_result.json()['video']['uuid']
                logging.info('{0}{1}/{2}'.format(PEERTUBE_ENDPOINT, '/videos/watch', video_uuid))
            except:
                logging.info(upload_result.text)
                sys.exit(1)
