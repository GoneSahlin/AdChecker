import sqlite3
import os

import utils

logger = utils.setup_logging('database')

DB_NAME = 'data.db'
DB_PATH = os.path.join('data', 'data.db')


def connect():
    cur = sqlite3.connect(DB_PATH)

    return cur

def create_database(cur):
    # create images table
    cur.execute('''
        create table if not exists Images (
           channel_name text,
           timestamp datetime,
           content blob,
           label text,
           label_timestamp,
           
           primary key(channel_name, timestamp)
        )
                   ''')

    cur.commit()
    logger.info('Images table created')

    cur.close()


if __name__ == '__main__':
    cur = connect()

    create_database(cur)

