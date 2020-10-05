from __init__ import AO3

def main():
    api = AO3()

    # test random public work
    public_work = api.work(20203051)
    print_stats(public_work)

    # test mature public work
    m_work = api.work(19712863)
    print_stats(m_work)

    pw = str(input('password: '))
    api.login('starrybouquet', pw)
    # test bookmarks
    bookmarks = api.user.bookmarks_ids()
    for i in range(4):
        print_stats(api.work(bookmarks[i]))
    # test restricted work
    restricted = api.work(24749773)
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
