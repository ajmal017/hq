#!/usr/bin/env python

from bs4 import BeautifulSoup
import os

with open("index.html") as fp:
    soup = BeautifulSoup(fp.read())

rows = soup.findAll('tr')
for r in rows:
    d = {}
    if r.attrs and 'id' in r.attrs:
        d.update(r.attrs)
        pair_id = r.attrs['id']
        a_tags = r.findAll('a')
        if len(a_tags) == 1:
            a_tag = a_tags[0]
            if a_tag.attrs:
                d.update(a_tag.attrs)
                d['text'] = a_tag.text
    # print d
    if not d:
        continue

    ss = '''    {"name": "%s",
    "code": "%s",
    "type": SecurityType.INDEX,
    "curr_id": %s,
    "page_url": "%s-historical-data",
    },
    ''' % (d['text'], os.path.basename(d['href']), d['id'].split("_")[1], d['href'])
    print ss.encode("utf-8")



