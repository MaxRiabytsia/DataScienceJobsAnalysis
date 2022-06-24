import pandas as pd
import pymysql
from bs4 import BeautifulSoup
import re
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from constants import *


def connect_to_db():
    connection = pymysql.connect(host=HOST, user=USERNAME, password=PASSWORD)

    if connection:
        print('Connected!')
        return connection
    else:
        raise Exception("Something went wrong...")


def get_job_title(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    title = page.find("h1", {"class": "icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title"})
    if title is None:
        return None
    return title.text


def get_company_name(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    name = page.find("div", {"class": "icl-u-textColor--success"})
    if name is None:
        return None
    return name.text


def get_company_rating(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    rating = page.find("div", {"class": "icl-Ratings icl-Ratings--sm icl-Ratings--gold"})
    if rating is None:
        return None
    rating = rating.find("meta")
    return rating["content"]


def get_number_of_reviews(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    number = page.find("div", {"class": "icl-Ratings-count"})
    if number is None:
        return None
    number = number.text
    number = int(re.sub('\D', '', number))
    return number


def get_indeed_salary_estimate(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    ul = page.find("ul", {"class": "css-1lyr5hv eu4oa1w0"})
    if ul is None:
        return None
    salary = ul.find_all("li")[1]
    salary = salary.text.replace(",", "")

    bounds = re.findall("\$\d{1,3}.?\d{1,3}K", salary)
    lower_bound = float(bounds[0][1:-1]) * 1000
    upper_bound = float(bounds[1][1:-1]) * 1000
    salary = int((lower_bound + upper_bound) / 2)

    return salary


def get_salary_from_employer(salary):
    salary_text = salary.text.replace(",", "")

    # if '-' is in salary text, then that is a range of salaries,
    # and we find the average
    if '-' in salary_text:
        dash_index = salary_text.find('-')
        lower_bound = float(re.findall("[-+]?(?:\d*\.\d+|\d+)", salary_text[:dash_index])[0])
        upper_bound = float(re.findall("[-+]?(?:\d*\.\d+|\d+)", salary_text[dash_index:])[0])
        salary = float((lower_bound + upper_bound) / 2)
    else:
        salary = float(re.findall("[-+]?(?:\d*\.\d+|\d+)", salary_text)[0])

    # transforming salary to annual format
    if "hour" in salary_text:
        salary = salary * 40 * 52
    elif "week" in salary_text:
        salary = salary * 52
    elif "month" in salary_text:
        salary = salary * 12

    return salary


def get_salary(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    # looking if there is salary from employer
    # if there is not, looking for Indeed's salary estimate
    salary = page.find("span", {"class": "icl-u-xs-mr--xs attribute_snippet"})
    if salary is None:
        return get_indeed_salary_estimate(job_info)
    else:
        return get_salary_from_employer(salary)


def get_company_location(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    div = page.find("div", {"class": "icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfo"
                                     "Header-subtitle jobsearch-DesktopStickyContainer-subtitle"})
    location = div.findChildren("div", recursive=False)[1].text

    if "Remote" in location:
        location = None

    return location


def is_remote(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    div = page.find("div", {
        "class": "icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfo"
                 "Header-subtitle jobsearch-DesktopStickyContainer-subtitle"})
    div_children = div.findChildren("div", recursive=False)

    if "remote" in div_children[1].text.lower() or "remote" in div_children[2].text.lower():
        return True
    return False


def is_full_time(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    div = page.find("div", {"id": "salaryInfoAndJobType"})
    if div is None:
        return True

    if "part-time" in div.text.lower():
        return False
    return True


def is_temporary(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    div = page.find("div", {"id": "salaryInfoAndJobType"})
    if div is None:
        return False

    if "temporary" in div.text.lower():
        return True
    return False


def is_internship(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    div = page.find("div", {"id": "salaryInfoAndJobType"})
    if div is None:
        return False

    if "internship" in div.text.lower():
        return True
    return False


def get_degree(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    description = page.find("div", {"class": "jobsearch-jobDescriptionText"})
    if description is None:
        return None
    description_text = description.get_text(separator="\n")
    description = tokenize(description_text)

    # we are starting with bachelor beacause when 2 degrees are mentioned in the description (e.g. bachelor and master)
    # the higher one is ussually 'prefered' not 'required'
    if "bachelor" in description or "ba" in description or "BS" in description_text.lower() or "b.s." in description:
        return "Bachelor"
    elif "master's" in description_text.lower() or "ms degree" in description:
        return "Master"
    elif "phd" in description or "doctoral" in description:
        return "PhD"
    elif "degree" in description:
        return "Bachelor"
    return "No degree"


def tokenize(text):
    # tokezation and lemmatization of the text
    lst = []
    tokenizer = RegexpTokenizer(r'\w+')
    tokenization = tokenizer.tokenize(text)
    wnl = WordNetLemmatizer()

    for token in tokenization:
        lst.append(wnl.lemmatize(token.lower()))

    return lst


def get_requirements(job_info):
    page = BeautifulSoup(job_info, 'html.parser')
    description = page.find("div", {"class": "jobsearch-jobDescriptionText"})
    if description is None:
        return None
    description = description.get_text(separator="\n")

    description = tokenize(description)

    requirements = set()
    for group_of_requirements in REQUIREMENTS:
        for requirement in group_of_requirements:
            for alias in requirement:
                if alias in description:
                    # when we find a requirement, we also count it as finding a group of requirements
                    requirements.add(requirement[0])
                    requirements.add(group_of_requirements[0][0])
                    break

    requirements = ",".join(requirements)

    if requirements != "":
        return requirements
    else:
        return None


def get_jobs_df(raw_jobs_df):
    jobs_df = pd.DataFrame(columns=["url", "job_title", "company_name", "company_rating", "number_of_reviews",
                                    "annual_salary", "location", "remote", "full_time", "temporary", "internship",
                                    "experience_level", "degree", "requirements"])

    for i, job in raw_jobs_df.iterrows():
        job_info = job.job_info
        jobs_df.loc[jobs_df.shape[0]] = pd.Series({
            "url": job.url,
            "job_title": get_job_title(job_info),
            "company_name": get_company_name(job_info),
            "company_rating": get_company_rating(job_info),
            "number_of_reviews": get_number_of_reviews(job_info),
            "annual_salary": get_salary(job_info),
            "location": get_company_location(job_info),
            "remote": is_remote(job_info),
            "full_time": is_full_time(job_info),
            "temporary": is_temporary(job_info),
            "internship": is_internship(job_info),
            "experience_level": job.experience_level,
            "degree": get_degree(job_info),
            "requirements": get_requirements(job_info)
        })

    return jobs_df


def main():
    # connect to database
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("USE jobs_db")

    raw_jobs_df = pd.read_sql("SELECT * FROM raw_jobs", connection)
    # raw_jobs_df = pd.read_pickle("data/raw_jobs_copy.pkl")

    jobs_df = get_jobs_df(raw_jobs_df)

    jobs_df.to_pickle("data/jobs.pkl")


if __name__ == "__main__":
    main()
