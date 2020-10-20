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

all_works = []
for id, work in all_works_html.items():
    work_item = Work(id, api.handler, load=False, soup=work)
    all_works.append(work_item)

api.to_json(all_works, 'first_200_works.txt')
