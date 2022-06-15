import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


LINK = "https://www.indeed.com/jobs?q=Data%20science&vjk=13aca544c07d9f80"
ENTRY_LEVEL_LINK = "https://www.indeed.com/jobs?q=Data%20science&sc=0kf%3Aexplvl(ENTRY_LEVEL)%3B&vjk=4013d246c0825159"
MID_LEVEL_LINK = "https://www.indeed.com/jobs?q=Data%20science&sc=0kf%3Aexplvl(MID_LEVEL)%3B&vjk=04020cf4e91f7ca0"
SENIOR_LEVEL_LINK = "https://www.indeed.com/jobs?q=Data%20science&sc=0kf%3Aexplvl(SENIOR_LEVEL)%3B&vjk=f1b835379c0f1cdd"
BASE_JOB_URL = "https://www.indeed.com/viewjob?"


# def is_captcha(page, class_name):
#     body = page.find("body", {"class": class_name})
#     if body is None:
#         return True
#     return False


def make_request(url):
    count = 0
    while count < 2:
        count += 1
        request = requests.get(url, "html.parser")
        print(request.status_code)
        if request.status_code == 200:
            return request
        else:
            print("Sleeping")
            time.sleep(30)

    return None


def get_all_page_links(page_number, link):
    request = make_request(link + f"&start={(page_number - 1) * 10}")
    if request is None:
        return None

    page = BeautifulSoup(request.content, "html.parser")

    last_page_text = page.find("p", {"class": "dupetext"})
    if last_page_text is not None:
        return None

    links = page.find_all("a", {"class": "jcs-JobTitle"})
    links = [i["href"][8:] for i in links]

    return links


def get_job_info(link):
    request = make_request(link)
    if request is None:
        return None

    page = BeautifulSoup(request.content, "html.parser")

    job_info = str(page.find("div", {
        "class": "jobsearch-ViewJobLayout-jobDisplay icl-Grid-col icl-u-xs-span12 icl-u-lg-span7"}))

    return job_info


def main():
    df = pd.DataFrame(columns=["url", "job_info", "experience_level"])
    lvl_links = [ENTRY_LEVEL_LINK, MID_LEVEL_LINK, SENIOR_LEVEL_LINK]
    lvl_names = ["Entry level", "Mid level", "Senior level"]
    for lvl_link, lvl_name in zip(lvl_links, lvl_names):
        page_number = 13  # 14 DONE
        while page_number < 15:
            print(page_number)
            links = get_all_page_links(page_number, lvl_link)
            if links is None:
                break
            page_number += 1
            for link in links:
                time.sleep(2)
                link = BASE_JOB_URL + link
                job_info = get_job_info(link)
                df.loc[df.shape[0]] = pd.Series({"url": link, "job_info": job_info, "experience_level": lvl_name})

    df = df.mask(df.eq('None')).dropna().reset_index(drop=True)
    df.to_csv("data/raw_jobs.csv", index=False)


if __name__ == "__main__":
    main()
