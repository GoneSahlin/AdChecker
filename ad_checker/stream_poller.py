import requests
import logging
import os
import cv2 as cv
import asyncio
from datetime import datetime, timedelta

from ad_checker import utils


logger = logging.getLogger()


async def poll_ts_file(poller_id: int, poll_queue: asyncio.PriorityQueue, decode_queue: asyncio.Queue):
    while True:
        logger.info(f'Starting poller {poller_id}')
        _, m3u, latest_ts_file = await poll_queue.get()
        logger.info(f'Poller {poller_id} running for m3u {m3u}')
        
        ts_url = utils.find_ts(m3u)

        if latest_ts_file and latest_ts_file == ts_url:
            logger.info(f'No new ts file found')
            timestamp = (datetime.now() - timedelta(seconds=1)).timestamp()  # wait 1 second

            await poll_queue.put((timestamp, m3u, ts_url))
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

                # create new jobs
                timestamp = (datetime.now() - timedelta(seconds=5)).timestamp()  # wait 5 seconds
                await poll_queue.put((timestamp, m3u, ts_url))
                await decode_queue.put(tmp_path)

            else:
                logger.error(f'Failed to get ts file, status code: {ts_response.status_code}')

        poll_queue.task_done()


