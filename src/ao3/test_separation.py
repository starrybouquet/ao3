from __init__ import AO3
from works_io import AO3PrivateHandler
import requests

def main():
    api = AO3()

    pw = str(input('password: '))
    # api.login('starrybouquet', pw)
    # test bookmarks
    # bookmarks = api.user.bookmarks_ids()
    # for i in range(4):
    #     print_stats(api.work(bookmarks[i]))

    priv_handler = AO3PrivateHandler(sess=requests.Session(), init_client=api)
    priv_handler.authenticate('starrybouquet', pw)
    # test restricted work
    restricted = api.work(24749773, io_handler=priv_handler, load=False)
    restricted.load_data()

    print_stats(restricted)


def print_stats(work):
    print('URL: ' + str(work.url))
    print('Title: ' + work.title)
    print('Author: ' + work.author)
    print('Summary:' + work.summary)
    print('Fandom: ' + str(work.fandoms))
    print('Stats: ')
    print('\t Published ' + str(work.published))
    print('\t Words ' + str(work.words))
    print('\t Comments ' + str(work.comments))
    print('\t Kudos ' + str(work.kudos))

main()
