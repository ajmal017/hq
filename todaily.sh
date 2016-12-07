#!/usr/bin/env bash

./todaily.py --filename=ALL --src-dir=sina_goods --dest-dir=sina_ohlc_daily --src-type=sinagoods
./todaily.py --filename=ALL --src-dir=hs_data --dest-dir=hs_ohlc_daily --src-type=hsindexs


./todaily.py --filename=ALL --src-dir=ohlc_debts --dest-dir=investing_ohlc_daily --src-type=investing
./todaily.py --filename=ALL --src-dir=ohlc_fxpros --dest-dir=investing_ohlc_daily --src-type=investing
./todaily.py --filename=ALL --src-dir=ohlc_goods --dest-dir=investing_ohlc_daily --src-type=investing
./todaily.py --filename=ALL --src-dir=ohlc_indexs --dest-dir=investing_ohlc_daily --src-type=investing
