import psycopg2
from error_logger import *
import os


def create_connection() -> object:
    """
    Function creates connection to database

    @return: connection object
    """
    try:
        if os.getenv('am_i_in_docker') is not None:
            conn = psycopg2.connect(user='postgres', host='my_postgres', password='admin')  # for docker
        else:
            conn = psycopg2.connect(user='postgres', host='localhost', port='65123', password='admin')  # for host pc
        return conn
    except Exception as e:
        print('Connect to database failed... Check logs')
        error_log(e)


def open_db(conn) -> None:
    """
    Function check if table is created, if not, create it

    @param: conn - connection to database
    """

    try:
        c = conn.cursor()
        # check if table is created, if not create it
        c.execute("""CREATE TABLE IF NOT EXISTS conversions (
                                                    timestamp VARCHAR(100),
                                                    date VARCHAR(10),
                                                    time VARCHAR(8),
                                                    pair VARCHAR(10),
                                                    rate real,
                                                    daily_change VARCHAR(1)
                                                    )""")
    except Exception as e:
        print('Failed to open database... Check logs')
        error_log(e)


def close_db(conn) -> None:
    """
    Function will close connection

    @param: conn - connection to database
    """
    try:
        c = conn.cursor()
        c.close()
        conn.close()
    except Exception as e:
        print('Failed to close database... Check logs')
        error_log(e)


def write(conn, data_for_db) -> None:
    """
    Function writes data to the database

    @param: conn - connection to database
    @param: data_for_db - list of data
    """
    try:
        c = conn.cursor()
        c.execute("INSERT INTO conversions VALUES (%s, %s, %s, %s, %s, %s)", (data_for_db['timestamp'],
                                                                              data_for_db['date'],
                                                                              data_for_db['time'],
                                                                              data_for_db['pair'],
                                                                              data_for_db['curr_convert_rate'],
                                                                              data_for_db['change']
                                                                              ))

        conn.commit()
    except Exception as e:
        print('Writing to the database failed... Check logs')
        error_log(e)


def read(conn: object) -> list:
    '''
    Function read necessary data from table and returns list of rows from db.

    @param: conn - connection to database
    @return: list of rows from database
    '''
    try:
        c = conn.cursor()
        c.execute("SELECT date, time, pair, rate, daily_change FROM conversions")
        rows = c.fetchall()
        return rows
    except Exception as e:
        print('Read from database failed... Check logs')
        error_log(e)
