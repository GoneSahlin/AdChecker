import os
import cv2 as cv
import logging

from ad_checker import utils

# logger = utils.setup_logging('test_utils', __name__)
logger = logging.getLogger()
logger.info('testing logger')

def test_get_latest_frame():
    logger.info('Starting test_get_latest_frame')
    # test_file_path = os.path.join('test', 'data', 'get_latest_frame_test.mp4')
    test_file_path = os.path.join('test', 'data', 'get_latest_frame_test.ts')

    # check that first frame has the correct size, if fails test file is broken
    vc = cv.VideoCapture(test_file_path)
    _, first_frame = vc.read()
    assert first_frame.size == 2764800
    
    # get latest_frame
    latest_frame = utils.get_latest_frame(vc)

    assert latest_frame is not None  # check that latest frame exists
    assert first_frame.size == 2764800  # check that latest frame has the correct size

    # debugging
    # cv.imshow('latest_frame', latest_frame)
    # cv.waitKey()

