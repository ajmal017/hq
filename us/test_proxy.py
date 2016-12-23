#!/usr/bin/env python
# http://stackoverflow.com/questions/12601316/how-to-make-python-requests-work-via-socks-proxy
import requests

proxies = {
  "http": "socks5://127.0.0.1:1080",
  "https": "socks5://127.0.0.1:1080",
}

url = "https://www.google.com.hk/finance/historical?q=NYSE:BABA"
r=requests.get(url, proxies=proxies)
print r.text
