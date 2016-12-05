#!/usr/bin/env python

from bs4 import BeautifulSoup
import os

with open("goods.html") as fp:
    soup = BeautifulSoup(fp.read())

rows = soup.findAll('tr')
for r in rows[1:]:
    d = {}
    tds = r.findAll("td")
    title1 = tds[0].findAll("span")[0].attrs['title']
    href = tds[1].findAll('a')[0].attrs['href']
    title2 = tds[1].findAll('a')[0].attrs['title']
    curr_id = tds[3].attrs['class'][0].split("-")[1]
    if title2.find(title1) < 0:
        title2 = title1 + title2

    ss = '''    {"name": "%s",
    "code": "%s",
    "type": SecurityType.GOODS,
    "curr_id": %s,
    "page_url": "%s-historical-data",
    },
    ''' % (title2, os.path.basename(href), curr_id, href)
    print ss.encode("utf-8")



