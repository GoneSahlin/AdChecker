import cv2 as cv
import requests

from ad_checker import utils, database


def main():
    url = 'https://livetv-fa.tubi.video/kcpq/index_1.m3u8'
    # url = 'https://livetv-fa.tubi.video/kcpq/index_2.m3u8'
    # url = 'https://livetv-fa.tubi.video/kcpq/index_3.m3u8'
    # url = 'https://livetv-fa.tubi.video/kcpq/index_4.m3u8'
    # url = 'https://livetv-fa.tubi.video/kcpq/index.m3u8'

    response = requests.get(url)
    if response.status_code == 200:
        print(response.text)
    else:
        print(response.status_code)
        print(response.text)

    try:
        ts = utils.find_ts(url)
        base_url = '/'.join(url.split('/')[:-1])
        ts_url = base_url + '/' + ts

        vc = cv.VideoCapture(ts_url)

        frame = utils.get_latest_frame(vc)

        cv.imshow('frame', frame)
        cv.waitKey()

    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()

