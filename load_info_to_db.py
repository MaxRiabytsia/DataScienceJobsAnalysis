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
    create_table_command = ("CREATE TABLE IF NOT EXISTS jobs (\n"
                            "		url VARCHAR(255) NOT NULL PRIMARY KEY,\n"
                            "		job_title VARCHAR(255),\n"
                            "		company_name VARCHAR(255),\n"
                            "		company_rating INT,\n"
                            "		number_of_reviews INT,\n"
                            "		annual_salary FLOAT,\n"
                            "		location VARCHAR(255),\n"
                            "		remote BOOLEAN,\n"
                            "		full_time BOOLEAN,\n"
                            "		temporary BOOLEAN,\n"
                            "		internship BOOLEAN,\n"
                            "		experience_level VARCHAR(255),\n"
                            "		degree VARCHAR(255),\n"
                            "		requirements VARCHAR(255)\n"
                            "	)")
    cursor.execute(create_table_command)
    cursor.connection.commit()


def insert_into_table(cursor, url, job_title, company_name, company_rating, number_of_reviews, annual_salary, location,
                      remote, full_time, temporary, internship, experience_level, degree, requirements):
    insert_row_command = (
        "INSERT IGNORE INTO jobs (url, job_title, company_name, company_rating, number_of_reviews, annual_salary, "
        "location, remote, full_time, temporary, internship, experience_level, degree, requirements) \n"
        "		VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    row_to_insert = (url, job_title, company_name, company_rating, number_of_reviews, annual_salary, location,
                     remote, full_time, temporary, internship, experience_level, degree, requirements)
    cursor.execute(insert_row_command, row_to_insert)
    cursor.connection.commit()


def append_from_df_to_db(cursor, df):
    for i, row in df.iterrows():
        insert_into_table(cursor, row['url'], row['job_title'], row['company_name'], row['company_rating'],
                          row['number_of_reviews'], row['annual_salary'], row['location'], row['remote'],
                          row['full_time'], row['temporary'], row['internship'], row['experience_level'],
                          row['degree'], row['requirements'])


def main():
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute("USE jobs_db")
    create_table(cursor)

    df = pd.read_pickle("data/jobs.pkl")
    append_from_df_to_db(cursor, df)


if __name__ == "__main__":
    main()
