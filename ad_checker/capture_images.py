import cv2 as cv
import requests
from datetime import datetime
import os
import time

from ad_checker import utils


# logging setup
logger = utils.setup_logging('capture_images.log')

def capture_images():
    logger.info('Starting')

    while True:
        try:
            response = requests.get('https://iptv-org.github.io/iptv/index.m3u')


            if response.status_code == 200:
                # getting image
                channel_name = 'fox_sports_1'

                url = utils.find_channel(response.text, channel_name)
                base_url = '/'.join(url.split('/')[:-1])

                m3u = utils.find_m3u(url)
                m3u_url = base_url + '/' + m3u

                print(m3u_url)
                return

                ts = utils.find_ts(m3u_url)
                ts_url = base_url + '/' + ts

                vc = cv.VideoCapture(ts_url)

                frame = utils.get_latest_frame(vc)

                # writing image
                dirpath = os.path.join('data', 'captured_images', channel_name)
                if not os.path.exists(dirpath):
                    os.mkdir(dirpath)

                time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                filepath = os.path.join(dirpath, time_str + '.png')

                logger.info(f'Writing image to {filepath}')
                cv.imwrite(filepath, frame)

                # wait before repeating
                time.sleep(15)
            else:
                raise Exception(f'Request failed with code {response.status_code}') 

        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    capture_images()

