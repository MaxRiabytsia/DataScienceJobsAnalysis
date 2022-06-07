import pymysql
import pandas as pd
from constants import *


def connect_to_db():
    connection = pymysql.connect(host=HOST, user=USERNAME, password=PASSWORD)

    if connection:
        print('Connected!')
        return connection
    else:
        raise Exception("Something went wrong...")


def create_table(cursor):
    create_table_command = ("CREATE TABLE IF NOT EXISTS raw_jobs (\n"
                            "		url VARCHAR(255) NOT NULL PRIMARY KEY,\n"
                            "		header VARCHAR(5000),\n"
                            "		body VARCHAR(5000),\n"
                            "		footer VARCHAR(5000)\n"
                            "	)")
    cursor.execute(create_table_command)
    cursor.connection.commit()


def insert_into_table(cursor, url, header, body, footer):
    insert_row_command = (
        "INSERT IGNORE INTO raw_jobs (url, header, body, footer) \n"
        "		VALUES (%s,%s,%s,%s)")
    row_to_insert = (url, header, body, footer)
    cursor.execute(insert_row_command, row_to_insert)
    cursor.connection.commit()


def append_from_df_to_db(cursor, df):
    for i, row in df.iterrows():
        insert_into_table(cursor, row['url'], row['job_header'], row['job_body'], row['job_footer'])


def main():
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute("USE jobs_db")
    create_table(cursor)

    df = pd.read_csv("data/raw_jobs.csv")
    append_from_df_to_db(cursor, df)


if __name__ == "__main__":
    main()
