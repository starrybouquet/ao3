import os
import sys
import random
import urllib.parse

from bs4 import BeautifulSoup
import pandas as pd

sys.path.insert(0, os.path.abspath('..'))

import ao3
from ao3.works import Work, iterate_pages

api = ao3.AO3()

api.login('starrybouquet')

pages = []
with open('data/hist.txt', 'r') as f:
    data = f.readlines()

current_html = '<!DOCTYPE html>'
for line in data[1:]:
    if '<!DOCTYPE html>' in line:
        pages.append(BeautifulSoup(current_html, 'html.parser'))
        current_html = '<!DOCTYPE html>'
    else:
        current_html += line
history = api.user.reading_history(hist_pages=pages)

history_df = pd.DataFrame(history, columns=['id', 'title', 'last read', 'word count'])
print(history_df.head())

history_df.to_csv('data/history_data.csv', index=False)
