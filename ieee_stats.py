# -*- coding: utf-8 -*-
"""
Created on 19:13 06/11/2016
@author: wsun2

using: PyCharm for project: StartUpTimes

Function description: parse the literatures exported from endnote, 1) into a dataframe 2) do some stats, mainly the keywors count
                      in order to better underhand the changes in trend
"""

import pandas as pd

def literature_stats(endnote_export_file):
    fname = endnote_export_file

    # full_dataitem = pd.DataFrame()

    with open(fname) as f:
        dataitem = {}
        df = pd.DataFrame()
        i = 0
        for line in f:  #
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
    df.to_csv('ieee_stats.csv')


    ieee_scotland = df.loc[df['Author Address'].str.contains('Scotland', na=False)]
    ieee_scotland.to_csv('ieee_scotland.csv')
    return df

def keywords_stats(df):
    keywords_header = [n for n in df.columns if ('Keywords' in n)]
    keywords_info = pd.Series()
    for keywords_iter in keywords_header:
        keywords_info = keywords_info.add(df[keywords_iter].value_counts(), fill_value=0)

    keywords_info.sort_values(inplace=True, ascending=False)
    keywords_info[keywords_info > 10].plot.bar()
    print keywords_info

    return keywords_info


def author_stats(df, country_list):
    for country in country_list:
        author_count = df['Author Address'].str.contains(country).sum()
        print '{} papers are from {}'.format(author_count, country)


if __name__ == "__main__":
    country_list = ['China', 'USA', 'England', 'Wales', 'Scotland', 'Edinburgh' ]

    meta_data_file = r'c:\Users\wsun2\Desktop\ieee_ps_2016.txt'
    literature = literature_stats(meta_data_file)
    keywords = keywords_stats(literature)
    author_stats(literature, country_list)
    keywords.to_csv('keywords_2016.csv')

meta_data_file = r'c:\Users\wsun2\Desktop\ieee_ps_2015.txt'
literature_2015 = literature_stats(meta_data_file)
keywords_2015 = keywords_stats(literature_2015)
author_stats(literature_2015, country_list)
keywords_2015.to_csv('keywords_2015.csv')


meta_data_file = r'c:\Users\wsun2\Desktop\ieee_ps_2016.txt'
literature_2016 = literature_stats(meta_data_file)
keywords_2016 = keywords_stats(literature_2016)
author_stats(literature_2016, country_list)

meta_data_file = r'c:\Users\wsun2\Desktop\ieee_ps_2013.txt'
literature_2013 = literature_stats(meta_data_file)
keywords_2013 = keywords_stats(literature_2013)
author_stats(literature_2013, country_list)

keywords_changes =  keywords_2016.subtract(keywords_2015,fill_value=0)
keywords_changes.sort_values(inplace=True, ascending=False)
print keywords_changes

keywords_changes =  keywords_2016.subtract(keywords_2013,fill_value=0)
keywords_changes.sort_values(inplace=True, ascending=False)
print keywords_changes

# the recent surge on 'robust optimization'
print keywords_2016['robust optimization']
print keywords_2015['robust optimization']
print keywords_2013['robust optimization']
print 'changes as follows:'
print keywords_changes['robust optimization']
print keywords_changes['robust optimization']
