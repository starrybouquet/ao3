from __init__ import AO3
import random
from bs4 import BeautifulSoup

def main():
    api = AO3()

    pw = str(input('password: '))
    api.login('starrybouquet', pw)
    # # get HTML
    # soups = api.handler.get_pages(api.user.username, 'bookmarks')
    # # save HTML
    # for n in range(len(soups)):
    #     with open("bookmark_html_{}.txt".format(n), "w") as f:
    #         plain_html = soups[n].prettify()
    #         f.write(plain_html)
    # input("HTML saved. Press 'enter' to continue.")

    # load HTML as soups
    soups = []
    for n in range(14):
        with open("html_save/bookmark_html_{}.txt".format(n), 'r') as f:
            html = f.read()
            soups.append(BeautifulSoup(html, 'html.parser'))
    print("Loaded soups. Getting bookmarks.")


    # test bookmarks - currently page_soups is passed in for debugging
    bookmarks = api.user.bookmarks(load=True, page_soups=soups)
    print("loaded bookmarks")
    input()

    for i in [random.randint(0, len(bookmarks)) for n in range(10)]:
        print_stats(bookmarks[n])

    print()

    # test restricted work
    restricted = api.work(24749773)
    restricted.load_data()
    print('Restricted: ')
    print_stats(restricted)


def print_stats(work):
    print('URL: ' + str(work.url))
    print('Title: ' + work.title)
    print('Title type ' + str(type(work.title)))
    print('Author: ' + work.author)
    print('Summary:' + work.summary)
    print('Fandom: ' + str(work.fandoms))
    print('Stats: ')
    print('\t Published ' + str(work.published))
    print('\t Words ' + str(work.words))
    print('\t Comments ' + str(work.comments))
    print('\t Kudos ' + str(work.kudos))

main()
