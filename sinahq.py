#!/usr/bin/env python

import requests

r = requests.get('http://hq.sinajs.cn/rn=1479737518332&list=hf_CHA50CFD,DINIW,hf_CL,hf_GC,hf_SI,hf_S,hf_C,hf_OIL,hf_CAD,hf_XAU,hf_XAG,hf_NG')

print r.text
