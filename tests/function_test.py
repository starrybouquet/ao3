import os
import sys
import random
import urllib.parse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath('..'))

import ao3
# from ao3.works import Work, iterate_pages
from ao3.users import User

api = ao3.AO3()

def test_init():
    api.login('starrybouquet')
    api.work('290290')

def test_user():
    api.login('starrybouquet')
    hist = api.user.reading_history()
    print(hist)

test_user()
