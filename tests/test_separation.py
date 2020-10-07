import os
import sys
import random
import urllib.parse

from bs4 import BeautifulSoup


sys.path.insert(0, os.path.abspath('..'))

import ao3
from ao3.users import User
from ao3.handlers import AO3Handler

def main():
    api = ao3.AO3()

    tag_name = "Samantha \"Sam\" Carter/Jack O'Neill"

    converted_tag = urllib.parse.quote(tag_name).replace('/', '*s*')
    pages = api.handler.get_pages('', 'tags', tag=converted_tag)

    # api.login('starrybouquet')
    # save_html(api, 'tag')

    # # load HTML as soups
    # soups = []
    # for n in range(14):
    #     with open("html_save/bookmark_html_{}.txt".format(n), 'r') as f:
    #         html = f.read()
    #         soups.append(BeautifulSoup(html, 'html.parser'))
    # print("Loaded soups. Getting bookmarks.")
    #
    #
    # # test bookmarks - currently page_soups is passed in for debugging
    # bookmarks = api.user.bookmarks(load=True, page_soups=soups)
    # print("loaded bookmarks")
    #
    # for i in [random.randint(0, len(bookmarks)) for n in range(10)]:
    #     work = bookmarks[i]
    #     print_stats(bookmarks[i])
    #
    # print()

    # test restricted work
    # restricted = api.work(24749773)
    # restricted.load_data()
    # print('Restricted: ')
    # print_stats(restricted)

def save_html(api, pagetype):
    # get HTML
    if pagetype == 'bookmarks':
        soups = api.handler.get_pages('', pagetype)
    elif pagetype == 'tag':
        soups = api.tag("Samantha \"Sam\" Carter/Jack O'Neill")
    # save HTML
    # for n in range(len(soups)):
    #     with open("html_save/{0}_html_{1}.txt".format(pagetype, n), "w") as f:
    #         plain_html = str(soups[n])
    #         f.write(plain_html)
    # input("HTML saved. Press 'enter' to continue.")
    return True

def print_stats(work):
    print('URL: ' + str(work.url))
    print('Title: ' + work.title)
    print('Author: ' + work.author)
    print('Summary:' + work.summary)
    print('Fandom: ' + str(work.fandoms))
    print('Icons: ')
    print('\t Rating ' + str(work.rating))
    print('\t Warnings ' + str(work.warnings))
    print('\t Category ' + str(work.category))
    print('Stats: ')
    print('\t Published ' + str(work.published))
    print('\t Posted Chapters ' + str(work.posted_chapters))
    print('\t Total Chapters ' + str(work.total_chapters))
    print('\t\t Complete? ' + str(work.complete))
    print('\t Words ' + str(work.words))
    print('\t Comments ' + str(work.comments))
    print('\t Kudos ' + str(work.kudos))

main()
