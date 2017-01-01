#!/usr/bin/env python
#-*-coding:utf-8-*-

import json
import sys
import os
import math
import datetime

import pandas as pd
import numpy as np
import matplotlib
if sys.platform.find("linux") >= 0:
    matplotlib.use('Agg')
else:
    matplotlib.use('TKAgg')
import matplotlib.colors as colors
import matplotlib.finance as finance
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.font_manager as font_manager
from pylab import mpl
mpl.rcParams['figure.figsize'] = [20, 12]
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
from matplotlib.lines import Line2D, TICKLEFT, TICKRIGHT
from matplotlib.patches import Rectangle

import matplotlib.cm as cmx
import matplotlib.colors as colors
from matplotlib.ticker import ScalarFormatter


def _cmap(N):
    '''
    Returns a function that maps each index in 0, 1, ... N-1 to a distinct
    RGB color.
    '''
    color_norm = colors.Normalize(vmin=0, vmax=N - 1)
    scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='hsv')

    def map_index_to_rgb_color(index):
        return scalar_map.to_rgba(index)
    return map_index_to_rgb_color


def main():
    ff = os.listdir("data")
    data = {}
    for f in ff:
        with open("data/%s" % f) as fp:
            t = json.loads(fp.read())
            year = int(f.split(".")[0])
            data[year] = {}
            for i in t:
                cty = i['country']
                gdp = i['gdp']
                if gdp.endswith(u"万亿"):
                    gdp = float(
                        gdp.replace(u'万亿', '').encode("utf-8")) * 100000
                elif gdp.endswith(u"亿"):
                    gdp = float(gdp.replace(u'亿', '').encode("utf-8")) * 10
                elif gdp.endswith(u'千万'):
                    gdp = float(gdp.replace(u'千万', '').encode("utf-8"))
                data[year][cty] = gdp

    N = 1
    YEARS = sorted(data.keys())
    topN = sorted(data[YEARS[-1]].items(),
                  key=lambda i: i[1], reverse=True)[:N]
    topN = [i[0] for i in topN]
    fig = plt.figure(figsize=(18, 12))
    ax1 = fig.add_subplot(111)
    ax1.set_title('GDP')
    # ax1.set_xlim(-1, len(YEARS) + 1)
    cmap = _cmap(N)
    for i in range(N):
        cty = topN[i]
        gdps = [data[year].get(cty, float("NAN")) for year in YEARS]
        line, = ax1.plot(YEARS, gdps)  # , color=cmap(i))
    ax1.set_yscale('log', basey=1.1)
    ax1.yaxis.set_major_formatter(ScalarFormatter())
    fig.savefig('%s_top_%s.png' % (YEARS[-1], N))

if __name__ == "__main__":
    main()
