import os
import sys
import random
import urllib.parse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath('..'))

import ao3
from ao3.works import Work, iterate_pages

api = ao3.AO3()

api.login('starrybouquet')
history = api.user.reading_history(save=True)

def wrap_items(l):
    return ['"' + str(i) + '"' for i in l]

csv_lines = [wrap_items(l) for item in history]
with open('data/history.csv', 'w') as file:
    for line in csv_lines:
        file.write(str(line)[1:len(line)-1] + '\n')
