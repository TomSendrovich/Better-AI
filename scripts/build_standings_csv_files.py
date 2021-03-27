import os
import re

from urllib.request import urlopen

# CONSTANTS
tr_pattern = "<tr>.*?</tr>"
title_pattern = "og:title\" content=\"(.*?)\."
team_name_pattern = "alt=\"(.*?),"
team_values_pattern = "align=\"center\">(.*?)<"
real_tr_pattern = "img"
tr_flags = re.S


def fetch_data(url, league, season):
    # get HTML from url
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")

    # get table from HTML
    table_index = html.find("<!-- Start Tabelle -->")
    start_index = table_index + len("<!-- Start Tabelle -->")
    end_index = html.find("<!-- Ende Tabelle -->")
    table = html[start_index:end_index]

    # get title from HTML
    title = re.findall(title_pattern, html)[0]
    title = title.replace('/', '-')

    # get relevant list
    tr_list = re.findall(tr_pattern, table, re.S)

    # open new file
    f = open(os.pardir + os.path.sep +
             "standings_csv" + os.path.sep +
             league + os.path.sep +
             str(season) + os.path.sep +
             title + ".csv", "w")

    f.write('#,Team,M,W,D,L,Goals,Diff,Pts\n')

    last_pos = 1
    for tr in tr_list:
        if len(re.findall(real_tr_pattern, tr)) != 0:
            team_name = re.findall(team_name_pattern, tr)[0]
            values = re.findall(team_values_pattern, tr)

            pos = values[0]
            if pos == '&nbsp;':
                pos = last_pos

            last_pos = pos

            f.write(pos)
            f.write(',' + team_name)
            f.write(',' + values[1])
            f.write(',' + values[2])
            f.write(',' + values[3])
            f.write(',' + values[4])
            f.write(',' + values[5])
            f.write(',' + values[6])
            f.write(',' + values[7])
            f.write('\n')

    f.close()

    print(title, "Done!")


def build_url(league, season, rnd):
    url = 'https://www.worldfootball.net/schedule/%s-%d-%d-spieltag/%d/' % (league, season, season + 1, rnd)
    return url


def build_url2(league, season, rnd):
    url = 'https://www.worldfootball.net/schedule/%s-%d-%d-spieltag_2/%d/' % (league, season, season + 1, rnd)
    return url


# eng-premier-league
for season in range(2010, 2021):
    for rnd in range(1, 39):
        url = build_url("eng-premier-league", season, rnd)
        fetch_data(url, "PL", season)

# esp-primera-division
for season in range(2010, 2020):
    for rnd in range(1, 39):
        url = build_url("esp-primera-division", season, rnd)
        if season == 2016:
            url = build_url2("esp-primera-division", season, rnd)

        fetch_data(url, "PD", season)
