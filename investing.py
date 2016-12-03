#!/usr/bin/env python

import requests
s = requests.Session()
s.headers.update(
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
    }
)

s.get('http://cn.investing.com/currencies/eur-usd-historical-data')


s.headers.update({
    "X-Requested-With": "XMLHttpRequest"
})
data = {"action": "historical_data",
        "curr_id": "1",
        "st_date": "2000/09/01",
        "end_date": "2016/12/02",
        "interval_sec": "Daily"}

r = s.post("http://cn.investing.com/instruments/HistoricalDataAjax",
           data=data)

print(r.text.encode("utf-8"))
