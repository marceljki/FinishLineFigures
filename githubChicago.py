import requests
from pyquery import PyQuery as pq
import pandas as pd
import re
import tqdm

BASE_URL = "https://results.chicagomarathon.com/2021/"
PATH = "?page={page}&event=MAR&lang=EN_CAP&num_results=1000&pid=list&search%5Bsex%5D={sex}&search%5Bage_class%5D=%25"


def parse_page(base_url, path, gender):
    resp = requests.get(base_url + path)
    d = pq(resp.content)
    # find first name field and navigate up to overarching row
    all_runners = d(".list-field.type-fullname a").closest(".list-group-item .row")
    all_runners_parsed = []
    for runner in all_runners.items():
        #     print(runner)
        name_country = runner.find(".type-fullname a").text()
        idp = re.search("(?<=idp=)[A-Z0-9_.-]*(?=&)", runner.find(".type-fullname a").attr['href']).group(0)
        details_url = base_url + "?content=detail&idp=" + idp
        data = {
            "name": name_country[:-6],
            "gender": gender,
            "country": name_country[-4:-1],
            "age_class": runner.find(".type-age_class").text().split("\n")[1],
            "half_time": runner.find(".type-time").eq(0).text().split("\n")[1],
            "finish_time": runner.find(".type-time").eq(1).text().split("\n")[1],
            "details_url": details_url,
        }
        all_runners_parsed.append(data)

    return all_runners_parsed


def get_details(details_url):
    x = pq(details_url)
    splits = {
        "start": {
            "time_of_day": x.find(".f-starttime_net.last").text(),
            "time": "00:00:00"
        },
        "5km": {
            "time_of_day": x.find(".f-time_05 .time_day").text(),
            "time": x.find(".f-time_05 .time").text()
        },
        "10km": {
            "time_of_day": x.find(".f-time_10 .time_day").text(),
            "time": x.find(".f-time_10 .time").text()
        },
        "15km": {
            "time_of_day": x.find(".f-time_15 .time_day").text(),
            "time": x.find(".f-time_15 .time").text()
        },
        "20km": {
            "time_of_day": x.find(".f-time_20 .time_day").text(),
            "time": x.find(".f-time_20 .time").text()
        },
        "half": {
            "time_of_day": x.find(".f-time_52 .time_day").text(),
            "time": x.find(".f-time_52 .time").text()
        },
        "25km": {
            "time_of_day": x.find(".f-time_25 .time_day").text(),
            "time": x.find(".f-time_25 .time").text()
        },
        "30km": {
            "time_of_day": x.find(".f-time_30 .time_day").text(),
            "time": x.find(".f-time_30 .time").text()
        },
        "35km": {
            "time_of_day": x.find(".f-time_35 .time_day").text(),
            "time": x.find(".f-time_35 .time").text()
        },
        "40km": {
            "time_of_day": x.find(".f-time_40 .time_day").text(),
            "time": x.find(".f-time_40 .time").text()
        },
        "finish": {
            "time_of_day": x.find(".f-time_finish_netto .time_day").text(),
            "time": x.find(".f-time_finish_netto .time").text()
        }
    }

    return {
        "bib": x.find(".f-start_no_text.last").text(),
        "city_state": x.find(".f-__city_state.last").text(),
        "splits": splits,
    }


all_runners = []

for page in tqdm.tqdm(range(1, 16)):
    all_runners += parse_page(BASE_URL, PATH.format(page=page, sex="M"), gender="man")

for page in tqdm.tqdm(range(1, 13)):
    all_runners += parse_page(BASE_URL, PATH.format(page=page, sex="W"), gender="woman")
