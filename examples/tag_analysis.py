import os
import sys
import random
import urllib.parse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath('..'))

import ao3
from ao3.works import Work, iterate_pages

api = ao3.AO3()

# load HTML as soups
soups = []
for n in range(1, 200):
    with open("html_save/tags_html_{}.txt".format(n), 'r') as f:
        html = f.read()
        soups.append(BeautifulSoup(html, 'html.parser'))
print("Loaded soups. Getting works.")

all_works_html = iterate_pages(soups, 'work', save_HTML=True)
assert (type(all_works_html) == dict)

all_works = []
for id, work in all_works_html.items():
    work_item = Work(id, api.handler, load=False, soup=work)
    # print("chapters: {}".format(work_item.chapters_posted))
    # print("total: {}".format(work_item.chapters_total))
    all_works.append(work_item)
c = input('do you want to continue?')
if c == 'y':
    api.to_csv(all_works, '200_works.csv')
