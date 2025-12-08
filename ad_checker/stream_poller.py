import requests
import logging
import os
import cv2 as cv

from ad_checker import utils


logger = logging.getLogger()


class StreamPoller:
    def __init__(self, m3u):
        self.m3u = m3u

        self.latest_ts_file = None

    def poll(self):
        ts_url = utils.find_ts(self.m3u)

        if self.latest_ts_file and self.latest_ts_file == ts_url:
            # no new ts file
            pass
        else:
            ts_response = requests.get(ts_url)

            if ts_response.status_code == 200:
                # save ts file into tmp
                tmp_path = os.path.join('/tmp', 'GoneSahlin', 'ad_checker', ts_url.removeprefix('https://'))
                os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
                with open(tmp_path, 'wb') as f:
                    response = requests.get(ts_url)
                    f.write(response.content)
                    logger.info('Retrieved and saved ts file into tmp path: {tmp_path}')

                vc = cv.VideoCapture(tmp_path)
                frame = utils.get_latest_frame(vc)

                cv.imshow('frame', frame)
                cv.waitKey()

            else:
                logger.error(f'Failed to get ts file, status code: {ts_response.status_code}')

