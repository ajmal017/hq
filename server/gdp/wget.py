#!/usr/bin/env python
#-*-coding:utf-8-*-
import time
import json
import requests
from bs4 import BeautifulSoup

def get(year):
    url = "http://www.kuaiyilicai.com/stats/global/yearly/g_gdp/%s.html" % year
    r = requests.get(url)
    s = BeautifulSoup(r.content)
    div = s.find("div", class_="table-responsive")
    trs = div.find_all("tr")
    rows = []
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) != 4:
            continue
        t = {
            "country": tds[0].text,
            "zhou": tds[1].text,
            "gdp": tds[2].text,
            "no": tds[3].text
            }
        rows.append(t)
    return rows

def main():
    for i in range(1960, 2016):
        rows = get(i)
        with open("data/%s.json" % i, "w") as fp:
            fp.write(json.dumps(rows))
        time.sleep(0.5)


if __name__ == "__main__":
    main()




