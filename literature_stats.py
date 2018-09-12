# -*- coding: utf-8 -*-
"""
Created on 19:13 06/11/2016
@author: wsun2

Function description: parse the literatures exported from endnote,
                    1) into a dataframe
                    2) do some stats, mainly the keywords count
                      in order to better underhand the changes in trend
"""

import pandas as pd
import matplotlib as mpl
import numpy as np
import numpy as np
# import geocoder
# from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from math import sqrt
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

# import setup_plt_style
# setup_plt_style.set_plt_style()

country_list = ['China', 'USA', 'England', 'Wales', 'Scotland', 'Edinburgh']


def find_contry(value, country_list):
    for country in country_list:
        if country in str(value):
            return country


# def plot_stat(s, scale = 1, title='USA stats'):  #todo: to fix; misundertood the function of geoparse; need a address as input, rather than just a name
#     map = Basemap(width=10000000, height=6000000, projection='lcc',
#                   resolution=None, lat_1=45., lat_2=55, lat_0=50, lon_0=-107.)
#     plt.figure(figsize=(19, 20))
#     for location, count in s.iteritems():
#         loc = geocoder.google(location)
#         if not loc:
#             print("Could not locate {}".format(location))
#             continue
#         x, y = map(loc.latlng[0], loc.latlng[1])
#         map.plot(x,y,marker='o',color='Red',markersize=int(sqrt(count))*scale)
#         plt.annotate(location, xy = (x,y), xytext=(-20,20))
#     plt.title(title)
#     plt.show()
#     plt.savefig('{}.png'.format(title))

def literature_stats(endnote_export_file):
    fname = endnote_export_file

    with open(fname) as f:
        dataitem = {}
        df = pd.DataFrame()
        i = 0
        for line in f:
            line_content = [n.strip() for n in line.strip().split(':', 1)]  #

            if line_content != ['']:
                if "," not in line_content[0]:
                    if len(line_content) == 1:
                        i += 1
                        line_content = ['Keywords_{0:02d}'.format(i), line_content[0]]
                    line_content = dict([line_content])
                    dataitem.update(line_content)  # print dataitem

            else:
                current = pd.DataFrame.from_dict(dataitem, orient='index')
                current = current.T
                df = df.append(current, ignore_index=True)
                dataitem = {}
                i = 0

    df_ = df['Author Address'].str.split(',', expand=True).iloc[:, 0]
    df_.name = 'University'  #
    df = pd.concat([df, df_], axis=1, sort=False)

    df['Country'] = df.apply(lambda row: find_contry(row['Author Address'], country_list), axis=1)  #
    # df['geo'] = df.apply(lambda row: geocoder.google(row['Author Address'] , axis=1)) #todo: to fix; wrong return datatype to insert into dataframe

    df.to_csv('stats_output\ieee_stats.csv')

    ieee_scotland = df.loc[df['Author Address'].str.contains('Scotland', na=False)]
    ieee_scotland.to_csv('stats_output\ieee_scotland.csv')

    ieee_usa = df.loc[df['Author Address'].str.contains('USA', na=False)]
    ieee_usa.to_csv('stats_output\ieee_USA.csv')
    return df


def keywords_stats(df, plot=True):
    keywords_header = [n for n in df.columns if ('Keywords' in n)]
    keywords_info = pd.Series()
    for keywords_iter in keywords_header:
        keywords_info = keywords_info.add(df[keywords_iter].value_counts(), fill_value=0)

    keywords_info.sort_values(inplace=True, ascending=False)

    try:
        if plot:
            with plt.style.context('grayscale'):
                plt.gray()
                keywords_info[keywords_info > 10].plot.barh()
                plt.grid('off')
                plt.tight_layout()
                plt.show()
        print(keywords_info)
    except:
        pass

    return keywords_info


def author_stats(df, country_list):
    for country in country_list:
        author_count = df['Author Address'].str.contains(country).sum()
        print('{} papers are from {}'.format(author_count, country))


def keywords_stats_horizon(df, horizon):
    keywords_stats_multiyears = pd.DataFrame()

    for year in horizon:
        if is_string_dtype(df['Year']):
            keywords_at_year = df[df['Year'] == str(year)]
        else:
            keywords_at_year = df[df['Year'] == int(year)]
        keywords_stats_at_year = keywords_stats(keywords_at_year, plot=False)
        keywords_stats_at_year.rename(year)
        keywords_stats_at_year = keywords_stats_at_year.to_frame(name=year)
        keywords_stats_multiyears = pd.concat([keywords_stats_multiyears, keywords_stats_at_year], axis=1, sort=False)

    keywords_stats_multiyears.fillna(0, inplace=True)

    keywords_stats_multiyears_changes = keywords_stats_multiyears.diff(periods=1, axis=1)
    keywords_stats_multiyears_changes.fillna(0, inplace=True)

    keywords_stats_multiyears_changes['abs_total'] = keywords_stats_multiyears_changes[horizon].abs().sum(axis=1)
    keywords_stats_multiyears_changes['total'] = keywords_stats_multiyears_changes[horizon].sum(axis=1)
    keywords_stats_multiyears_changes.sort_values(by=['total', 'abs_total'], ascending=False, inplace=True)
    print('\n changes in trends top10 \n')
    print(keywords_stats_multiyears_changes.head(10))
    print('\n changes in trends last10 \n')
    print(keywords_stats_multiyears_changes.tail(10))

    keywords_stats_multiyears['total'] = keywords_stats_multiyears.sum(axis=1)
    keywords_stats_multiyears.sort_values(by='total', ascending=False, inplace=True)
    print('\ntotal in trends top10 \n')
    print(keywords_stats_multiyears.head(20))
    print(' \ntotal in trends last10 \n')
    print(keywords_stats_multiyears.tail(10))

    return keywords_stats_multiyears, keywords_stats_multiyears_changes


def plot_keywords_stats_multiyears(keywords_stats_multiyears, horizon, keywords):
    colors = plt.cm.rainbow(np.linspace(0, 1, len(keywords)))
    if keywords:
        for keyword, c in zip(keywords, colors):
            keywords_stats_multiyears[keywords_stats_multiyears.index.str.contains(keyword)][horizon].sum().plot(label=keyword)
    else:
        keywords_stats_multiyears.head(10).T.loc[horizon].plot()
    plt.legend(loc=0)
    return plt


def print_keywords_stats(keywords_stats_multiyears_changes, keywords_stats_multiyears, horizon, keywords):
    for keyword in keywords:
        print('\n=====================================')
        print('\n the summary of {}'.format(keyword))
        print('=====================================')

        print(keywords_stats_multiyears_changes[keywords_stats_multiyears_changes.index.str.contains(keyword)].sum())
        print('\n')
        print(keywords_stats_multiyears[horizon][keywords_stats_multiyears.index.str.contains(keyword)].sum())


# todo: to finish
def author_stats_horizon(df, horizon):
    author_stats_multiyears = pd.DataFrame()
    for year in horizon:
        author_at_year = df[df['Year'] == year]
        author_stats_at_year = author_stats(author_at_year)  # ...


if __name__ == "__main__":
    pass
