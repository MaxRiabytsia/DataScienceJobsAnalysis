import pandas as pd
import pymysql
from bs4 import BeautifulSoup
from constants import *


def connect_to_db():
    connection = pymysql.connect(host=HOST, user=USERNAME, password=PASSWORD)

    if connection:
        print('Connected!')
        return connection
    else:
        raise Exception("Something went wrong...")


def get_job_title(job):
    header = BeautifulSoup(job.header, 'html.parser')
    title = header.find("h1", {"class": "icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title"})
    return title.text


def get_company_name(job):
    footer = BeautifulSoup(job.footer, 'html.parser')
    name = footer.find("div", {"class": "icl-u-textColor--success"})
    return name.text


def get_company_rating(job):
    header = BeautifulSoup(job.header, 'html.parser')
    rating = header.find("div", {"class": "icl-Ratings icl-Ratings--sm icl-Ratings--gold"})
    if rating is None:
        return None
    rating = rating.find("meta")
    return rating["content"]


def get_jobs_df(raw_jobs_df):
    jobs_df = pd.DataFrame(columns=["url", "job_title", "company_name", "company_rating", "number_of_reviews",
                                    "annual_salary", "location", "remote", "full-time", "temporary", "internship",
                                    "years_of_experience", "degree", "requirements"])

    for i, job in raw_jobs_df.iterrows():
        jobs_df.loc[jobs_df.shape[0]] = pd.Series({
            "url": job.url,
            "job_title": get_job_title(job),
            "company_name": get_company_name(job),
            "company_rating": get_company_rating(job),
            "number_of_reviews": 0,
            "annual_salary": 0,
            "location": 0,
            "remote": 0,
            "full-time": 0,
            "temporary": 0,
            "internship": 0,
            "years_of_experience": 0,
            "degree": 0,
            "requirements": 0
        })

    return jobs_df


def main():
    # connect to database
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("USE jobs_db")

    raw_jobs_df = pd.read_sql("SELECT * FROM raw_jobs", connection)

    jobs_df = get_jobs_df(raw_jobs_df)

    jobs_df.to_csv("data/jobs.csv")


if __name__ == "__main__":
    main()
