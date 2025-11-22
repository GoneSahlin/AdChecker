import os
import cv2 as cv
from datetime import datetime
import numpy as np

from ad_checker import utils
from ad_checker import database


logger = utils.setup_logging('label_images.log')


def images_to_label(channel_name):
    conn = database.connect()
    cur = conn.cursor()

    sql = '''
        select image_id, content
        from images
        -- where label is null
        where label = 'other' 
            and channel_name = ?
        order by timestamp
        limit 1000
        '''

    cur.execute(sql, (channel_name,))
    rows = cur.fetchall()
    conn.close()

    return rows


def insert_labels(labels_dict: dict[int, str]):
    """Store labels_dict (image_id, label) in db"""
    rows = [(item[1], item[0]) for item in labels_dict.items()]

    conn = database.connect()
    
    sql = '''
        update Images
        set label = ?
        where image_id = ?
        '''

    conn.executemany(sql, rows)
    conn.commit()
    conn.close()


def label_images(channel_name):
    logger.info('Getting images to label')
    images = images_to_label(channel_name)

    labels_dict = {}

    logger.info('Displaying images')
    i = 0
    while i < len(images):
        image_id, content = images[i]

        try:
            # display image
            img = utils.bytes_to_image(content)

            cv.imshow('frame', img)
            key_pressed = cv.waitKey(0)

            # handle user input
            input_mapping_dict = {
                'a': 'ad',
                'f': 'football',
                'b': 'basketball',
                'r': 'racing',
                's': 'soccer',
                't': 'talk',
                'o': 'other',
            }

            while chr(key_pressed) not in input_mapping_dict.keys() and chr(key_pressed) not in ['q', 'u']:
                key_pressed = cv.waitKey(0)

            if key_pressed == ord('q'):
                break
            elif key_pressed == ord('u'):
                i -= 1
                continue
            else:
                label = input_mapping_dict[chr(key_pressed)]

            # save label to dict
            logger.info(f'Labeling image {image_id} as {label}')
            labels_dict[image_id] = label

            i += 1
        except AssertionError as e:
            logger.error(e)

    # save labels to db
    logger.info('Saving labels to db')
    insert_labels(labels_dict)



if __name__ == '__main__':
    logger.info('Starting')
    
    label_images('fox_sports_1')

    logger.info('Ending')

