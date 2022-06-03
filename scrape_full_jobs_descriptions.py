import requests
from bs4 import BeautifulSoup as bs
import pandas as pd


LINK = "https://www.indeed.com/jobs?q=Data%20science&vjk=13aca544c07d9f80"
BASE_JOB_URL = "https://www.indeed.com/viewjob?"


def get_all_page_links(page_number):
    request = requests.get(LINK + f"&start={(page_number - 1) * 10}", "html.parser")
    page = bs(request.content, "html.parser")

    last_page_text = page.find("p", {"class": "dupetext"})
    if last_page_text is not None:
        return None

    links = page.find_all("a", {"class": "jcs-JobTitle"})
    links = [i["href"][8:] for i in links]

    return links


def get_job_header_and_body(link):
    request = requests.get(link, "html.parser")
    page = bs(request.content, "html.parser")
    header = str(page.find("div", {"class": "jobsearch-DesktopStickyContainer"}))
    body = str(page.find("div", {"id": "jobDescriptionText"}))

    return header, body


def main():
    df = pd.DataFrame(columns=["url", "job_header", "job_body"])
    page_number = 1
    while True:
        print({page_number})
        links = get_all_page_links(page_number)
        if links is None:
            break
        page_number += 1
        for link in links:
            link = BASE_JOB_URL + link
            header, body = get_job_header_and_body(link)
            df.loc[df.shape[0]] = pd.Series({"url": link, "job_header": header, "job_body": body})

    df.to_csv("data/raw_jobs.csv")


if __name__ == "__main__":
    main()
