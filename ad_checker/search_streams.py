import requests
from bs4 import BeautifulSoup
import json
import cv2 as cv
from datetime import datetime
import io
import os

from ad_checker import utils
from ad_checker.stream_poller import StreamPoller


logger = utils.setup_logging('search_streams', __name__)

def league_streams_page(league):

    base_url = 'https://crackstreams.cfd/'
    league_streams_page_url = base_url + 'league/' + league

    logger.info(f'Getting {league} league streams page')
    response = requests.get(league_streams_page_url)

    stream_page_urls = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        for tag in soup.find_all('a'):
            href = str(tag['href'])
            if href and href[:8] == '/stream/':
                stream_page_url = base_url + href
                stream_page_urls.append(stream_page_url)

    else:
        logger.error('Failed to get {league} league streams page, status code: {response.status_code}')

    logger.info(f'Found {len(stream_page_urls)} stream page urls')

    return stream_page_urls


def stream_page(stream_page_url):
    logger.info(f'Getting stream page {stream_page_url}')
    response = requests.get(stream_page_url)
    if response.status_code == 200:
        key = 'php?channel='
        offset = len(key)
        start_index = response.text.find(key) + offset
        end_index = response.text[start_index:].find('"') + start_index

        channel = response.text[start_index:end_index]

        logger.info(f'Found channel: {channel}')
        return channel

    else:
        logger.error(f'Failed to get stream page {stream_page_url}, status code: {response.status_code}')


def get_playlist_m3us(channel):
    logger.info(f'Getting playlist_m3us for channel {channel}')

    url = f'https://sharkstreams.net/get-stream.php?channel={channel}'

    response = requests.get(url)

    if response.status_code == 200:
        json_obj = json.loads(response.text)

        playlist_m3us = json_obj['urls']

        logger.info(f'Found {len(playlist_m3us)} playlist_m3us for channel {channel}')
        return playlist_m3us
    else:
        logger.error(f'Failed to get playlist_m3us for channel {channel}, status code: {response.status_code}')

# stream page -> channels
# split on channels
    # channel -> playlist_m3us
    # playlist_m3u -> m3u -> ts -> frame

def main():
    logger.info('Starting')

    league = 'nfl-streams'
    # league = 'nba'

    stream_page_urls = league_streams_page(league)

    frames_dict = {}
    for stream_page_url in stream_page_urls:
        channel = stream_page(stream_page_url)

        if channel:
            playlist_m3us = get_playlist_m3us(channel)

            if playlist_m3us:
                for playlist_m3u in playlist_m3us:
                    try:
                        logger.info(f'Getting m3u from playlist_m3u: {playlist_m3u}')
                        m3u = utils.find_m3u(playlist_m3u)
                        logger.info(f'Found m3u from playlist_m3u: {playlist_m3u}')

                        poller = StreamPoller(m3u)
                        poller.poll()


                        # logger.info(f'Getting ts from m3u: {m3u}')
                        # ts_url = utils.find_ts(m3u)
                        # logger.info(f'Found ts url: {ts_url}')
                        #
                        # ts_response = requests.get(ts_url)
                        # if ts_response.status_code == 200:
                        #     tmp_path = os.path.join('/tmp', 'GoneSahlin', 'ad_checker', ts_url.removeprefix('https://'))
                        #     os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
                        #     with open(tmp_path, 'wb') as f:
                        #         response = requests.get(ts_url)
                        #         f.write(response.content)
                        #         logger.info('Retrieved and saved ts file into temp path: {tmp_path}')
                        #
                        # else:
                        #     logger.error('Failed to retrieve and save ts file')
                        #     raise Exception('Failed to retrieve and save ts file')
                        #
                        # vc = cv.VideoCapture(tmp_path)
                        #
                        # frame = utils.get_latest_frame(vc)
                        # frames_dict[stream_page_url] = frame
                        #
                    except Exception as e:
                        logger.error(f'Failed to process playlist_m3u: {playlist_m3u}, {e}')

    logger.info(frames_dict)

if __name__ == '__main__':
    main()

