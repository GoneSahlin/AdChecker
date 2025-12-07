import cv2 as cv
import requests
import logging
import os
import numpy as np


# logger = logging.getLogger('__main__.utils')
logger = logging.getLogger()


def setup_logging(filename, name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    log_path = os.path.join('logs', filename)
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def find_channel(text, key):
    lines = text.split('\n')

    for line in lines:
        if key in line.lower():
            return line.strip()

    raise Exception(f'Unable to find {key}')


def find_m3u(url):
    response = requests.get(url)

    if response.status_code == 200:
        lines = response.text.split('\n')

        for line in lines:
            if 'm3u' in line:
                return line.strip()

        raise Exception(f'Unable to find m3u in response text:\n{response.text}')

    else:
        raise Exception(f'Request failed with code {response.status_code}') 


def find_ts(url):
    response = requests.get(url)

    if response.status_code == 200:
        lines = response.text.split('\n')

        ts_lines = filter(lambda x: 'ts' in x, lines)

        if not ts_lines:
            raise Exception(f'Unable to find m3u in response text:\n{response.text}')

        logger.debug(lines)
        most_recent_ts = sorted(ts_lines)[-1]

        return most_recent_ts.strip()

    else:
        raise Exception(f'Request failed with code {response.status_code}') 


def get_latest_frame(vc):
    logger.debug(f'Starting get_latest_frame')
    num_frames = int(vc.get(cv.CAP_PROP_FRAME_COUNT))
    logger.debug(f'num_frames: {num_frames}')

    vc.set(cv.CAP_PROP_POS_FRAMES, num_frames - 1)
    ret, frame = vc.read()

    frames_from_end = 0
    while not ret:
        logger.debug(f'Failed to read frame, moving back')
        frames_from_end += 1

        vc.set(cv.CAP_PROP_POS_FRAMES, num_frames - 1 - frames_from_end)
        ret, frame = vc.read()

    return frame


def play_video(url):
    vc = cv.VideoCapture(url)

    while(vc.isOpened()):
        # Capture frame-by-frame
        ret, frame = vc.read()
        if ret == True:

            # Display the resulting frame
            cv.imshow('Frame',frame)

            # Press Q on keyboard to  exit
            if cv.waitKey(25) == ord('q'):
                break

            # Break the loop
        else: 
            break


def bytes_to_image(image_bytes):
    logger.info('Converting bytes to image')
    image_array = np.asarray(bytearray(image_bytes))
    image = cv.imdecode(buf=image_array, flags=cv.IMREAD_COLOR)

    assert image is not None
    return image


