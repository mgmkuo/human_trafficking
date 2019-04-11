#!/usr/bin/python3

"""
Scrapes Backpage webpages. 
Saves to csv with column names:
    post_id
    date: date ad was posted
    time: time ad was posted
    age
    gender
    phone
    region
    loc0 - 7: for additional location information

"""
import argparse
from bs4 import BeautifulSoup
import datetime
import os
import io
import re
import sys


def extract_post_id(soup):
    post_id = soup.find_all('div', attrs={'style':'padding-left:2em;'})
    if post_id:
        post_id = re.findall('Post ID: ([0-9]*)', str(post_id))[0]
    return post_id

def extract_time_stamp(soup):
    time_stamp = soup.find(attrs={'class':'adInfo'})
    if time_stamp:
       time_stamp = re.findall('[MTWFS].*[APM]', time_stamp.text)
       time_stamp = str(datetime.datetime.strptime(time_stamp[0], "%A, %B %d, %Y %I:%M %p"))
       return time_stamp.split(' ')
    else:
        return '',''


def extract_age(soup):
    age = soup.find('p', class_='metaInfoDisplay')
    if age:
        return re.findall('[0-9]+', str(age))[0]
    else:
        return ''


def extract_gender(soup):
    gender = ''
    for item in soup.select('li > a'):
        if 'data-key' in str(item):
            gender = item['data-key']
    return gender


def extract_phone(soup):
    phone = soup.find('div', class_='postingBody')
    if phone:
        return re.findall(':.(.[0-9)-].*)<', str(phone))[0]
    else:
        return ''


def extract_area(soup):
    return re.findall('[a-z]+', soup.li.a['href'])[1]


def extract_loc(soup):
    loc = soup.find('div', attrs={'style':'padding-left:2em;'})
    if loc:
        loc = re.findall('Location:\s*([A-Za-z, ]*)', loc.text)[0]
    else:
        loc = 'empty'
    return loc

def create_header(max_col):
    header = 'post_id, date, time, age, gender, phone, area'
    for i in range(1, max_col+1):
        header += ',loc_{}'.format(i)
    return header

def extract(soup, max_col):
    post_id = extract_post_id(soup)
    date, time = extract_time_stamp(soup)
    age = extract_age(soup)
    gender = extract_gender(soup)
    phone = extract_phone(soup)
    area = extract_area(soup)
    loc = extract_loc(soup)
    row = '\n' + post_id \
            + ',' + date \
            + ',' + time \
            + ',' + age \
            + ',' + gender \
            + ',' + phone \
            + ',' + area \
            + ',' + loc
    if loc:
        max_col = len(loc.split(',')) if len(loc.split(',')) > max_col else max_col
    else:
        max_col = max_col
 
    return row, max_col

def create_csv(folder):
    data = io.StringIO()
    errors = open(os.path.join(os.getcwd(), 'error_log.txt'), 'w')
 
    max_col = 1
    counter = 0
    for f in os.listdir(folder):
        with open(os.path.join(folder, f)) as fp:
            soup = BeautifulSoup(fp, 'lxml')
        try:
            row, max_col = extract(soup, max_col)
            data.write(row)
            print('{} files processed: {}'.format(counter, f))
        except (TypeError, IndexError):
            errors.write('\n{}'.format(f))
        counter += 1
   
    errors.close()
    header = create_header(max_col)
    with open(os.path.join(os.getcwd(), 'backpage_data.csv'), 'w') as f:
        f.write(header)
        f.write(data.getvalue())
        data.close()
        f.close()
        print('\nData written to {}'.format(os.path.join(os.getcwd(), 'backpage_data.csv')))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    arg = parser.parse_args()
    create_csv(arg.folder)
