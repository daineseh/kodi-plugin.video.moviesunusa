# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
from collections import OrderedDict

import re
import requests
import urlparse


GOOGLE_URL = 'https://drive.google.com/file/d/'
BUILD_GOOGLE_URL = lambda x: urlparse.urljoin(GOOGLE_URL, x).encode('utf8')

BASE_URL = 'http://2d-gate.org'
BUILD_URL = lambda x: urlparse.urljoin(BASE_URL, x).encode('utf8')


class Series:
    def __init__(self, name, url, thumb):
        self.name = self._to_str_type(name)
        self.url = self._to_str_type(url)
        self.thumb = self._to_str_type(thumb)

    def _to_str_type(self, value):
        if not value:
           return

        if isinstance(value, str):
           return value
        return value.encode('utf8')

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @property
    def thumb(self):
        return self.__thumb

    @thumb.setter
    def thumb(self, value):
        self.__thumb = value


class ParseMovieSunUSA:
    def __init__(self, url=None):
        if url:
            self.url = url
        else:
            self.url = "http://moviesunusa.com/"
        self.req = requests.get(self.url)
        self.soup = BeautifulSoup(self.req.text, 'html.parser')

    def get_hot(self):
        hot = []
        for li_tag in self.soup.find_all('li', {'class':'carousel-item'}):
            print(li_tag)
            a_tag = li_tag.find('a')
            if not a_tag:
                continue
            img_tag = a_tag.find('img')
            if img_tag.get('srcset'):
                img = img_tag.get('srcset').split(',')[-1].strip().split(' ')[0]
            else:
                img = img_tag.get('src')
            hot.append(Series(a_tag.get('title'), a_tag.get('href'), img))
        return hot

    def new_arrivals(self):
        new = []
        for div_tag in self.soup.find_all('div', {'class':'cp-thumb'}):
            a_tag = div_tag.find('a')
            if not a_tag:
                continue
            img_tag = a_tag.find('img')
            img = img_tag.get('srcset').split(',')[-1].strip().split(' ')[0]
            new.append(Series(a_tag.get('title'), a_tag.get('href'), img))
        return new

    def get_episodes(self):
        episodes = []
        thumb = ''
        for p_tag in self.soup.find_all('p'):
            a_tag = p_tag.find('a')
            if not a_tag:
                continue
            img_tag = a_tag.find('img')
            if not img_tag:
                continue
            thumb = img_tag.get('src')

        for strong_tag in self.soup.find_all('strong'):
            a_tag = strong_tag.find('a')
            if not a_tag:
                continue
            name = a_tag.get('title')
            if not name:
                continue
            episodes.append(Series(name, a_tag.get('href'), thumb))
        return episodes

    def get_films(self):
        films = []
        pat = re.compile("http[s]?://(videomega.tv|openload.co|www.dailymotion.com)([a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        for i in pat.finditer(self.req.text):
            films.append(i.group())
        return films

    def get_list(self, value1, value2):
        content = OrderedDict()
        div_tag = self.soup.find('div', {'class': "hp-main"})
        part1_tag = div_tag.find('div', {'class': value1})
        for item in part1_tag.find_all('div', {'class': value2}):
            field = item.find('h4').string
            list_item = content.setdefault(field, [])
            for a_tag in item.find_all('a'):
                list_item.append(Series(a_tag.string, a_tag.get('href'), None))
        return content

    def list_of_part1(self):
        class_value1 = "hp-sidebar hp-home-8"
        class_value2 = "sb-widget home-8"
        return self.get_list(class_value1, class_value2)

    def list_of_part2(self):
        class_value1 = "hp-sidebar sb-right hp-home-9"
        class_value2 = "sb-widget home-9"
        return self.get_list(class_value1, class_value2)

    def list_of_part3(self):
        class_value1 = "hp-sidebar sb-right hp-home-10"
        class_value2 = "sb-widget home-10"
        return self.get_list(class_value1, class_value2)


if __name__ == '__main__':
    obj = ParseMovieSunUSA()

