import re
import collections
from datetime import datetime

from .handlers import AO3Handler
from .works import iterate_pages, Work


ReadingHistoryItem = collections.namedtuple(
    'ReadingHistoryItem', ['work_id', 'title', 'last_read', 'word_count'])


class User(object):
    """AO3 User object.

    Parameters
    ----------
    username : str
        AO3 username.
    password : str
        AO3 password. Does not check if it is correct.
    public_handler : AO3PublicHandler()
        Public handler for loading works, etc.
    sess : Session
        requests Session to use

    Attributes
    ----------
    io_handler : AO3UserHandler
        Handler for the user's I/O
    username : str
        AO3 username.

    """

    def __init__(self, username, handler):
        self.username = username
        self.io_handler = handler
        self._bookmarks_loaded = False

    def __repr__(self):
        return '%s(username=%r)' % (type(self).__name__, self.username)

    def bookmarks_ids(self):
        """User.bookmark_ids() --> list

        Returns a list of the user's bookmarks' ids. Ignores external work bookmarks.

        User must be logged in to see private bookmarks.

        Returns
        -------
        list
            List of work ids bookmarked by the user.
        """

        bookmarks = []
        num_works = 0

        page_soups = self.io_handler.get_pages(self.username, 'bookmarks')
        bookmarks = iterate_pages(page_soups, 'bookmark')

        return bookmarks

    def bookmarks(self, load=False, page_soups=None):
        """User.bookmark_ids() --> list

        Returns a list of the user's bookmarks' ids. Ignores external work bookmarks.

        User must be logged in to see private bookmarks.

        Returns
        -------
        list
            List of work ids bookmarked by the user.
        """

        bookmarks = []
        num_works = 0
        if page_soups == None:
            page_soups = self.io_handler.get_pages('starrybouquet', 'bookmarks')

        bookmarks_data = iterate_pages(page_soups, 'bookmark', save_HTML=True)
        if load: # load works from given HTML - no I/O required
            bookmarks = []

            for id, html in bookmarks_data.items():
                # print('n = {0} \t loading bookmark with id {1}'.format(n, bookmark_id))
                work = Work(id, io_handler=self.io_handler, load=False, soup=html)
                bookmarks.append(work)

                num_works += 1
                # print (str(bookmark_total) + "\t bookmarks found.")
            return bookmarks

        else: # just return IDs and html
            return bookmarks_data

    def load_bookmarks(self):
        """User.load_bookmarks() --> list

        Returns a list of the user's bookmarks as Work objects.

        Takes forever.

        User must be logged in to see private bookmarks.

        Returns
        -------
        list
            List of user's book as Work objects.

        """

        bookmark_total = 0
        bookmark_ids = self.bookmarks_ids()
        bookmarks = []

        for bookmark_id in bookmark_ids:
            work = Work(bookmark_id, io_handler=self.io_handler)
            bookmarks.append(work)

            bookmark_total = bookmark_total + 1
            # print (str(bookmark_total) + "\t bookmarks found.")

        return bookmarks

    def reading_history(self):
        """User.reading_history() --> list

        Returns a list of articles in the user's reading history.

        This requires the user to turn on the Viewing History feature..

        Returns
        -------
        list
            List of ``ReadingHistoryItem`` instances,
            a 4-tuple ``(work_id, title, last_read, word_count)``.

        """
        # TODO: What happens if you don't have this feature enabled?

        # URL for the user's reading history page
        api_url = (
            'https://archiveofourown.org/users/%s/readings?page=%%d' %
            self.username)

        hist_pages = self.io_handler.get_pages(self.username, 'history')
        history_items = []

        for page in hist_pages:

            # The entries are stored in a list of the form:
            #
            #     <ol class="reading work index group">
            #       <li id="work_12345" class="reading work blurb group">
            #         ...
            #       </li>
            #       <li id="work_67890" class="reading work blurb group">
            #         ...
            #       </li>
            #       ...
            #     </ol>
            #
            ol_tag = page.find('ol', attrs={'class': 'reading'})
            for li_tag in ol_tag.findAll('li', attrs={'class': 'blurb'}):
                try:
                    work_id = li_tag.attrs['id'].replace('work_', '')

                    # Within the <li>, the last viewed date is stored as
                    #
                    #     <h4 class="viewed heading">
                    #         <span>Last viewed:</span> 24 Dec 2012
                    #
                    #         (Latest version.)
                    #
                    #         Viewed once
                    #     </h4>
                    #
                    h4_tag = li_tag.find('h4', attrs={'class': 'viewed'})
                    date_str = re.search(
                        r'[0-9]{1,2} [A-Z][a-z]+ [0-9]{4}',
                        h4_tag.contents[2]).group(0)
                    date = datetime.strptime(date_str, '%d %b %Y').date()
                    h4_title = self._soup.find('h4', attrs={'class': 'heading'})
                    title = h4_title.find_all('a')[0].get_text().strip()
                    word_count = li_tag.find('dd', attrs={'class': 'words'}).text

                    history_items.append(ReadingHistoryItem(work_id, title, date, word_count))
                except KeyError:
                    # A deleted work shows up as
                    #
                    #      <li class="deleted reading work blurb group">
                    #
                    # There's nothing that we can do about that, so just skip
                    # over it.
                    if 'deleted' in li_tag.attrs['class']:
                        pass
                    else:
                        raise

        return history_items
