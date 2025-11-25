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


def register_adapters():
    sqlite3.register_adapter(datetime, adapt_datetime_iso)


def connect():
    register_adapters()
    conn = sqlite3.connect(DB_PATH)

    return conn


def move_to_database(channel_name):
    conn = connect()

    # read files
    images_path = os.path.join('data', 'captured_images', 'fox_sports_1')
    files = os.listdir(images_path)

    def row_generator(channel_name, files):
        for file in files:
            filepath = os.path.join(images_path, file)

            with open(filepath, 'rb') as f:
                content = f.read()

                formatted_timestamp = datetime.strptime(file, '%Y-%m-%d_%H-%M-%S.png')

                yield channel_name, formatted_timestamp, content

    sql = '''
        insert or ignore into images(channel_name, timestamp, content)
        values (?, ?, ?);
        '''

    conn.executemany(sql, row_generator(channel_name, files))
    conn.commit()
    conn.close()


def create_database(conn):
    # create channels table
    conn.execute('''
        create table if not exists Channels (
            channel_id integer primary key autoincrement,
            channel_name text,
            m3u text,

            unique (channel_name)
        )
    ''')

    # create images table
    conn.execute('''
        create table if not exists Images (
            image_id integer primary key autoincrement,
            channel_id integer,
            timestamp datetime,
            content blob,
            label text,
            label_timestamp datetime,

            unique (channel_id, timestamp),
            foreign key (channel_id) references Channels(channel_id)
        )
    ''')

    conn.commit()

    logger.info('Images table created')

    conn.close()


if __name__ == '__main__':
    conn = connect()

    create_database(conn)
    # move_to_database('fox_sports_1')

