import os
import cv2 as cv
from datetime import datetime

import utils


logger = utils.setup_logging('label_images.log')


def load_labels() -> pl.DataFrame:
    labels_filepath = os.path.join('data', 'labels', 'labels.parquet')

    try:
        df = pl.read_parquet(labels_filepath)
    except FileNotFoundError as e:
        schema = {'key': str, 'channel_name': str, 'filename': str, 'label': str, 'timestamp': datetime}

        df = pl.DataFrame(schema=schema)


    return df


def label_images(channel_name):
    logger.info('Starting')

    captured_images_dir = os.path.join('data', 'captured_images', channel_name)

    files = os.listdir(captured_images_dir)

    labels_df = load_labels()

    i = 0
    while i < len(files):
        file = files[i]

        if file in labels_df['filename']:
            i += 1
            continue

        try:
            filepath = os.path.join(captured_images_dir, file)

            logger.info(f'Reading from {filepath}')
            img = cv.imread(filepath)

            assert img is not None, "file could not be read, check with os.path.exists()"

            cv.imshow('frame', img)

            labels_dict = {
                'a': 'ad',
                'f': 'football',
                'o': 'other',
            }

            # handle user input
            key_pressed = cv.waitKey(0)
            while chr(key_pressed) not in labels_dict.keys() and chr(key_pressed) not in ['q', 'u']:
                key_pressed = cv.waitKey(0)

            if key_pressed == ord('q'):
                break
            elif key_pressed == ord('u'):
                i -= 1
                continue
            else:
                label = labels_dict[chr(key_pressed)]

            logger.info(f'Marked {file} as {label}')

            row = (channel_name + '|' + file, channel_name, file, label, datetime.now())



            i += 1
            

        except AssertionError as e:
            logger.error(e)


if __name__ == '__main__':
    logger.info('Starting')
    raise Exception('Test Error')

    
    label_images('fox_sports_1')

