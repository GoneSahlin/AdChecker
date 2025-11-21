import sqlite3
from datetime import datetime
import os

from ad_checker import utils

logger = utils.setup_logging('database')

DB_NAME = 'data.db'
DB_PATH = os.path.join('data', 'data.db')


def adapt_datetime_iso(val):
    """Adapt datetime.datetime to timezone-naive ISO 8601 date."""
    return val.replace(tzinfo=None).isoformat()


def connect():
    conn = sqlite3.connect(DB_PATH)

    return conn


def create_database(conn):
    # create images table
    conn.execute('''
        create table if not exists Images (
            image_id integer primary key autoincrement,
            channel_name text,
            timestamp datetime,
            content blob,
            label text,
            label_timestamp datetime,

            unique (channel_name, timestamp)
        )
    ''')

    conn.commit()

    logger.info('Images table created')

    conn.close()


if __name__ == '__main__':
    conn = connect()

    create_database(conn)

