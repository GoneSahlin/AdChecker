import requests
import logging
import os
import cv2 as cv
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass

from ad_checker import utils


logger = logging.getLogger()


@dataclass
class Channel:
    m3u: str
    latest_ts_file: str | None
    channel_id: int 


async def poll_ts_file(poller_id: int, poll_queue: asyncio.PriorityQueue[tuple[float, Channel]], decode_queue: asyncio.Queue):
    while True:
        logger.info(f'Starting poller {poller_id}')
        next_run_timestamp, channel = await poll_queue.get()
        logger.info(f'Poller {poller_id} running for channel {channel.channel_id}')

        time_to_next_run = next_run_timestamp - datetime.now().timestamp()
        if time_to_next_run > 0:
            logger.info(f'Poller {poller_id} sleeping for {time_to_next_run} seconds')
            await asyncio.sleep(time_to_next_run)
        
        ts_url = await asyncio.to_thread(utils.find_ts, channel.m3u)

        if channel.latest_ts_file and channel.latest_ts_file == ts_url:
            logger.info(f'No new ts file found')
            timestamp = (datetime.now() + timedelta(seconds=1)).timestamp()  # wait 1 second

            await poll_queue.put((timestamp, channel))
        else:
            ts_response = await asyncio.to_thread(requests.get, ts_url)

            if ts_response.status_code == 200:
                # save ts file into tmp
                tmp_path = os.path.join('/tmp', 'GoneSahlin', 'ad_checker', ts_url.removeprefix('https://'))
                tmp_path = os.path.join('/tmp', 'GoneSahlin', 'ad_checker', str(channel.channel_id), ts_url.split('/')[-1])
                os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
                with open(tmp_path, 'wb') as f:
                    response = requests.get(ts_url)
                    f.write(response.content)
                    logger.info(f'Retrieved and saved ts file into tmp path: {tmp_path}')

                # create new jobs
                timestamp = (datetime.now() - timedelta(seconds=3)).timestamp()  # wait 5 seconds
                channel.latest_ts_file = ts_url
                await poll_queue.put((timestamp, channel))
                await decode_queue.put(tmp_path)

            else:
                logger.error(f'Failed to get ts file, status code: {ts_response.status_code}')
                timestamp = (datetime.now() + timedelta(seconds=1)).timestamp()  # wait 1 second
                await poll_queue.put((timestamp, channel))

        poll_queue.task_done()


