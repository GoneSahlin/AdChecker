import cv3 as cv
import requests
from datetime import datetime
import os
import time

from ad_checker import utils, database


# logging setup
logger = utils.setup_logging('capture_images.log')

def capture_images():
    logger.info('Starting')

    # channel_name = 'cbs_7_seattle_wa'
    channel_name = 'fox_13_seattle_wa'

    m3u = database.get_m3u(channel_name)
    logger.info(f'Retrieved m3u for {channel_name}: {m3u}')

    # print(requests.get(m3u).text)
    # return

    ts = utils.find_ts(m3u)
    base_url = '/'.join(m3u.split('/')[:-1])
    ts_url = base_url + '/' + ts

    vc = cv.VideoCapture(ts_url)

    frame = utils.get_latest_frame(vc)

    # writing image
    dirpath = os.path.join('data', 'captured_images', channel_name)
    if not os.path.exists(dirpath):
        logger.info(f'Creating directory: {dirpath}')
        os.mkdir(dirpath)

    time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filepath = os.path.join(dirpath, time_str + '.png')

    logger.info(f'Writing image to {filepath}')
    cv.imwrite(filepath, frame)

    # wait before repeating
    time.sleep(15)


if __name__ == '__main__':
    capture_images()

