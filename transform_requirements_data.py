import pandas as pd
import pymysql
from constants import *


def connect_to_db():
    connection = pymysql.connect(host=HOST, user=USERNAME, password=PASSWORD)

    if connection:
        print('Connected!')
        return connection
    else:
        raise Exception("Something went wrong...")


def get_requirements_df(df):
    requirements_df = pd.DataFrame(columns=["group_of_requirements", "requirement", "experience_level", "degree",
                                            "remote", "full_time", "temporary", "internship", "number_of_occurrences"])

    # here we fill in 'requirements' dataset
    # 'requirements' dataset is a table that keeps track of requirements' occurrences
    # based on filters such as experience_level, degree, remote, etc.
    for group in REQUIREMENTS:
        for requirement in group:
            for exp_lvl in EXPERIENCE_LEVELS:
                for degree in DEGREES:
                    for remote in [True, False]:
                        for full_time in [True, False]:
                            for temporary in [True, False]:
                                for internship in [True, False]:
                                    df0 = df.loc[(df.experience_level == exp_lvl) & (df.degree == degree) &
                                                 (df.remote == remote) & (df.full_time == full_time) &
                                                 (df.temporary == temporary) & (df.internship == internship)]

                                    count = 0
                                    for i, row in df0.iterrows():
                                        if row.requirements is not None:
                                            if requirement[0] in row.requirements:
                                                count += 1

                                    requirements_df.loc[requirements_df.shape[0]] = pd.Series({
                                        "group_of_requirements": group[0][0],
                                        "requirement": requirement[0],
                                        "experience_level": exp_lvl,
                                        "degree": degree,
                                        "remote": remote,
                                        "full_time": full_time,
                                        "temporary": temporary,
                                        "internship": internship,
                                        "number_of_occurrences": count
                                    })

    return requirements_df


def main():
    # connect to database
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("USE jobs_db")
    df = pd.read_sql("SELECT * FROM jobs", connection)

    requirements_df = get_requirements_df(df)
    requirements_df.to_pickle("data/requirements.pkl")


if __name__ == "__main__":
    main()
