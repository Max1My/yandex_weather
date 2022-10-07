import sqlite3
import datetime
from sqlite3 import OperationalError


def create_db():
    conn = sqlite3.connect('weather')
    c = conn.cursor()

    c.execute('''
              CREATE TABLE IF NOT EXISTS results
              ([result_id] INTEGER PRIMARY KEY AUTOINCREMENT,[city_name] TEXT, [date_time_request] TIMESTAMP, [status] BOOLEAN)
              ''')

    conn.commit()
    c.close()
    conn.close()


def insert_into_table(value,city_name):
    currentDateTime = datetime.datetime.now()
    try:
        connection = sqlite3.connect('weather',
                                     detect_types=sqlite3.PARSE_DECLTYPES |
                                                  sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()

        # create query to insert the data
        insertQuery = """INSERT INTO results(city_name,date_time_request,status)
            VALUES (? ,?, ?);"""

        # insert the data into table
        cursor.execute(insertQuery, (city_name,currentDateTime, value))
        print("Data Inserted Successfully !")

        # commit the changes,
        # close the cursor and database connection
        connection.commit()
        cursor.close()
        connection.close()
    except OperationalError:
        create_db()
        insert_into_table(value,city_name)