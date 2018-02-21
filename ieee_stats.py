# -*- coding: utf-8 -*-
"""
Created on 19:13 06/11/2016
@author: wsun2

using: PyCharm for project: StartUpTimes

Function description: parse the literatures exported from endnote, 1) into a dataframe 2) do some stats, mainly the keywors count
                      in order to better underhand the changes in trend
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import geocoder
import setup_plt_style
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from math import sqrt
from datetime import datetime

setup_plt_style.set_plt_style()

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
    # status_indicator = 0
    fname = endnote_export_file

    # full_dataitem = pd.DataFrame()

    with open(fname) as f:
        dataitem = {}
        df = pd.DataFrame()
        i = 0
        for line in f:  #
            # status_indicator += 1
            # print status_indicator
            line_content = [n.strip() for n in line.strip().split(':', 1)]  #

            if line_content != ['']:
                if "," not in line_content[0]:
                    if len(line_content) == 1:
                        i += 1
                        line_content = ['Keywords_{0:02d}'.format(i), line_content[0]]
                    # print line_content
                    line_content = dict([line_content])
                    dataitem.update(line_content)
                    # print dataitem

            else:
                current = pd.DataFrame.from_dict(dataitem, orient='index')
                current = current.T
                df = df.append(current, ignore_index=True)
                dataitem = {}
                i = 0

    df_ = df['Author Address'].str.split(',', expand=True).iloc[:,0]
    df_.name = 'University' #
    df = pd.concat([df, df_], axis=1)

    df['Country'] = df.apply(lambda row: find_contry(row['Author Address'], country_list) , axis=1) #
    # df['geo'] = df.apply(lambda row: geocoder.google(row['Author Address'] , axis=1)) #todo: to fix; wrong return datatype to insert into dataframe

    df.to_csv('stats_output\ieee_stats.csv')

    ieee_scotland = df.loc[df['Author Address'].str.contains('Scotland', na=False)]
    ieee_scotland.to_csv('stats_output\ieee_scotland.csv')

    ieee_usa = df.loc[df['Author Address'].str.contains('USA', na=False)]
    ieee_usa.to_csv('stats_output\ieee_USA.csv')
    return df


def keywords_stats(df):
    keywords_header = [n for n in df.columns if ('Keywords' in n)]
    keywords_info = pd.Series()
    for keywords_iter in keywords_header:
        keywords_info = keywords_info.add(df[keywords_iter].value_counts(), fill_value=0)

    keywords_info.sort_values(inplace=True, ascending=False)
    # keywords_info[keywords_info > 10].plot.bar()
    # print keywords_info

    return keywords_info


def author_stats(df, country_list):
    for country in country_list:
        author_count = df['Author Address'].str.contains(country).sum()
        print '{} papers are from {}'.format(author_count, country)


def keywords_stats_horizon(df, horizon):
    keywords_stats_multiyears = pd.DataFrame()
    for year in horizon:
        keywords_at_year = df[df['Year'] == year]
        keywords_stats_at_year = keywords_stats(keywords_at_year)
        keywords_stats_at_year.rename(year)
        keywords_stats_at_year = keywords_stats_at_year.to_frame(name=year)
        # print keywords_stats_at_year.head()
        keywords_stats_multiyears = pd.concat([keywords_stats_multiyears, keywords_stats_at_year], axis=1)
        # print keywords_stats_multiyears.head()

    keywords_stats_multiyears.fillna(0, inplace=True)

    keywords_stats_multiyears_changes = keywords_stats_multiyears.diff(periods=1, axis=1)
    keywords_stats_multiyears_changes.fillna(0, inplace=True)

    keywords_stats_multiyears_changes['abs_total'] = keywords_stats_multiyears_changes[horizon].abs().sum(axis=1)
    keywords_stats_multiyears_changes['total'] = keywords_stats_multiyears_changes[horizon].sum(axis=1)
    keywords_stats_multiyears_changes.sort_values(by=['total', 'abs_total'], ascending=False, inplace=True)
    print '\n changes in trends top10 \n'
    print keywords_stats_multiyears_changes.head(10)
    print '\n changes in trends last10 \n'
    print keywords_stats_multiyears_changes.tail(10)

    keywords_stats_multiyears['total'] = keywords_stats_multiyears.sum(axis=1)
    keywords_stats_multiyears.sort_values(by='total', ascending=False, inplace=True)
    print '\ntotal in trends top10 \n'
    print keywords_stats_multiyears.head(20)
    print ' \ntotal in trends last10 \n'
    print keywords_stats_multiyears.tail(10)

    keywords_stats_multiyears_changes.to_csv('stats_output\keywords_stats_multiyears_changes.csv')
    keywords_stats_multiyears.to_csv('stats_output\keywords_stats_multiyears.csv')

    def plot_keywords_stats_multiyears(keywords):
        for keyword in keywords:
            keywords_stats_multiyears[keywords_stats_multiyears.index.str.contains(keyword)][horizon].sum().plot(label=keyword)
        plt.legend(loc=0)
        plt.ylim(0, 70)
        plt.title('the count of keywords in IEEE trans Power system')
        plt.show()

    def print_keywords_stats(keywords):
        for keyword in keywords:
            print '\n====================================='
            print '\n the summary of {}'.format(keyword)
            print '====================================='

            print keywords_stats_multiyears_changes[keywords_stats_multiyears_changes.index.str.contains(keyword)].sum()
            print '\n'
            print keywords_stats_multiyears[horizon][keywords_stats_multiyears.index.str.contains(keyword)].sum()

    # keywords_interested = ['distributed gen', 'price', 'active network', 'natural gas', 'reserve', 'capacity value', 'uncertainty', 'robust optimization', 'demand side','demand respon']
    # keywords_interested = ['distributed gen', 'price',  'natural gas', 'uncertainty', 'robust optimization', 'agent', 'demand respon', 'game theory']
    keywords_interested = ['distributed gen', 'natural gas', 'uncertainty', 'robust optimization', 'storage', 'demand respon']  # 'active networ' is not a ieee keywords
    plot_keywords_stats_multiyears(keywords_interested)
    print_keywords_stats(keywords_interested)


# todo: to finish
def author_stats_horizon(df, horizon):
    author_stats_multiyears = pd.DataFrame()
    for year in horizon:
        author_at_year = df[df['Year'] == year]
        author_stats_at_year = author_stats(author_at_year)
        # ...


if __name__ == "__main__":
    country_list = ['China', 'USA', 'England', 'Wales', 'Scotland', 'Edinburgh']

# meta_data_file = r'metadata\ieee_sg_all.txt'
meta_data_file = r'metadata\ieee_ps_sg_all.txt' # combination of ps and sg
literature = literature_stats(meta_data_file)
ieee = literature

select_ = ieee[ieee['Country'] == 'USA']['University'].value_counts()
select_.to_csv('USA universities stats')
print(select_[select_>1].nlargest(20))
# plot_stat(ieee[ieee['Country'] == 'USA']['University'].value_counts(), 5) #todo: function to be fixed
# ieee.to_csv('stats_output\ieee_sg_dirt.csv')
ieee.to_csv('stats_output\ieee_comb.csv')
#
# frac = min(len(ieee_ps) * 0.05, 20)
# ieee_ps.dropna(thresh=frac, axis=1, inplace=True)
# ieee_ps.to_csv('stats_output\ieee_sg_clean.csv')

ieee = pd.read_csv('stats_output\ieee_clean.csv', header=0)
horizon = list(range(2011, 2017, 1))
# horizon = [str(n) for n in horizon] # for smart grid metadata
keywords_stats_horizon(ieee, horizon)
author_stats(ieee, country_list)

# todo: one shot run
# ieee['Year'] = ieee['Year'].astype(np.int64)

# meta_data_file = r'metadata\ieee_2015.txt'
# literature_2015 = literature_stats(meta_data_file)
# keywords_2015 = keywords_stats(literature_2015)
# author_stats(literature_2015, country_list)
# keywords_2015.to_csv('stats_output\keywords_2015.csv')


# meta_data_file = r'metadata\ieee_2016.txt'
# literature_2016 = literature_stats(meta_data_file)
# keywords_2016 = keywords_stats(literature_2016)
# author_stats(literature_2016, country_list)
#
# meta_data_file = r'metadata\ieee_2013.txt'
# literature_2013 = literature_stats(meta_data_file)
# keywords_2013 = keywords_stats(literature_2013)
# author_stats(literature_2013, country_list)
#
# keywords_changes =  keywords_2016.subtract(keywords_2015,fill_value=0)
# keywords_changes.sort_values(inplace=True, ascending=False)
# print keywords_changes
#
# keywords_changes =  keywords_2016.subtract(keywords_2013,fill_value=0)
# keywords_changes.sort_values(inplace=True, ascending=False)
# print keywords_changes
#
# # the recent surge on 'robust optimization'
# print keywords_2016['robust optimization']
# print keywords_2015['robust optimization']
# print keywords_2013['robust optimization']
# print 'changes as follows:'
# print keywords_changes['robust optimization']
# print keywords_changes['robust optimization']

# horizon = [2016]
# keywords_stats_horizon(literature,[2016])

# stats_outputs = r'metadata\paper\ieee_stats_all - clean.csv'
# stats_outputs = r'metadata\paper\ieee_stats_all - clean.csv'
# ieee = pd.read_csv(stats_outputs,header=0)

# horizon = [2008, 2009, 2010,2011,2012,2013,2014,2015,2016]
# horizon = [2015,2016]
