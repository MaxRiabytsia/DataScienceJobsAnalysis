import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from constants import *

# link for page of jobs
LINK = "https://www.indeed.com/jobs?q=Data%20science"
# base link for individual of jobs
BASE_JOB_URL = "https://www.indeed.com/viewjob?"


def get_levels_links():
    request = make_request(LINK)
    if request is None:
        return []

    page = BeautifulSoup(request.content, "html.parser")
    ul = page.find_all("ul", {"id": "filter-explvl-menu"})
    if ul is None:
        return []

    links = ul[0].find_all("a", {"class": "yosegi-FilterPill-dropdownListItemLink"})
    if links is None:
        return []

    links = [LINK + i["href"][20:] for i in links]

    # returning in correct order
    return [links[2], links[0], links[1]]


def make_request(url):
    count = 0
    # when we can't get the page (i.e. the code is not 200)
    # we wait and try again (because CAPTCHA might be the reason)
    # if the request fails again, we wait again to prevent possible CAPTCHA on the next page
    while count < 2:
        count += 1
        request = requests.get(url, "html.parser")
        print(request.status_code)
        if request.status_code == 200:
            return request
        else:
            print("Sleeping")
            time.sleep(5)

    return None


def get_all_page_links(page_number, link):
    request = make_request(link + f"&start={(page_number - 1) * 10}")
    if request is None:
        return None

    page = BeautifulSoup(request.content, "html.parser")

    # trying to find text that appears only on the last page
    # if result is None, we could not find it
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

    # string conversion is here because we will load this data to a database which does not support bs4 data types
    job_info = str(page.find("div", {
        "class": "jobsearch-ViewJobLayout-jobDisplay icl-Grid-col icl-u-xs-span12 icl-u-lg-span7"}))

    return job_info


def main():
    df = pd.DataFrame(columns=["url", "job_info", "experience_level"])
    # I decided that it would be easier to get required experience levels for jobs by using Indeed filters
    # rather than scraping this information from jobs' descriptions
    # that is why I iterate over URLs with different level filter
    lvl_links = get_levels_links()
    for lvl_link, lvl_name in zip(lvl_links, EXPERIENCE_LEVELS):
        # In order to avoid receiving a CAPTCHA I added few time.sleep() functions
        # for a few seconds to imitate human browsing speed.
        time.sleep(5)
        page_number = 1  # 59 DONE
        while True:
            print(page_number)
            # links is None when function detects text that says that this page is the last one
            links = get_all_page_links(page_number, lvl_link)
            if links is None:
                break
            page_number += 1
            for link in links:
                time.sleep(1)
                link = BASE_JOB_URL + link
                job_info = get_job_info(link)
                df.loc[df.shape[0]] = pd.Series({"url": link, "job_info": job_info, "experience_level": lvl_name})

    # when request fails we can get 'None' in the table, here I drop those rows
    df = df.mask(df.eq('None')).dropna().reset_index(drop=True)
    df.to_csv("data/raw_jobs.csv", index=False)


if __name__ == "__main__":
    main()
