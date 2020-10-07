import os
import sys
import random
import urllib.parse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath('..'))

import ao3


api = ao3.AO3()

# load HTML as soups
soups = []
for n in range(1, 200):
    with open("html_save/tags_html_{}.txt".format(n), 'r') as f:
        html = f.read()
        soups.append(BeautifulSoup(html, 'html.parser'))
print("Loaded soups. Getting works.")

all_works = iterate_pages(soups, 'work', saveHTML=True)

api.to_csv(all_works, '200_works.csv')
