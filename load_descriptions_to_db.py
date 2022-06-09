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
                            "		job_info VARCHAR(15000),\n"
                            "		experience_level VARCHAR(16)\n"
                            "	)")
    cursor.execute(create_table_command)
    cursor.connection.commit()


def insert_into_table(cursor, url, job_info, experience_level):
    insert_row_command = (
        "INSERT IGNORE INTO raw_jobs (url, job_info, experience_level) \n"
        "		VALUES (%s,%s,%s)")
    row_to_insert = (url, job_info, experience_level)
    cursor.execute(insert_row_command, row_to_insert)
    cursor.connection.commit()


def append_from_df_to_db(cursor, df):
    for i, row in df.iterrows():
        insert_into_table(cursor, row['url'], row['job_info'], row['experience_level'])


def main():
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute("USE jobs_db")
    create_table(cursor)

    df = pd.read_csv("data/raw_jobs.csv")
    append_from_df_to_db(cursor, df)


if __name__ == "__main__":
    main()
