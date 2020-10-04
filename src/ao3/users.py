from .user_io import AO3UserHandler


ReadingHistoryItem = collections.namedtuple(
    'ReadingHistoryItem', ['work_id', 'last_read'])


class User(object):

    def __init__(self, username, password, sess=None):
        self.username = username
        self.io_handler = AO3UserHandler(self, sess)

    def __repr__(self):
        return '%s(username=%r)' % (type(self).__name__, self.username)

    def bookmarks_ids(self):
        """
        Returns a list of the user's bookmarks' ids. Ignores external work bookmarks.

        User must be logged in to see private bookmarks.
        """

        bookmarks = []
        num_works = 0

        page_soups = self.io_handler.get_bookmark_pages(self.username, 'bookmarks')
        for page in page_soups:
            # print("Finding page: \t" + str(page_no) + " of bookmarks. \t" + str(num_works) + " bookmarks ids found.")

            # The entries are stored in a list of the form:
            #
            #     <ol class="bookmark index group">
            #       <li id="bookmark_12345" class="bookmark blurb group" role="article">
            #         ...
            #       </li>
            #       <li id="bookmark_67890" class="bookmark blurb group" role="article">
            #         ...
            #       </li>
            #       ...
            #     </o

            ol_tag = page.find('ol', attrs={'class': 'bookmark'})


            for li_tag in ol_tag.findAll('li', attrs={'class': 'blurb'}):
                num_works = num_works + 1
                try:
                    # <h4 class="heading">
                    #     <a href="/works/12345678">Work Title</a>
                    #     <a href="/users/authorname/pseuds/authorpseud" rel="author">Author Name</a>
                    # </h4>

                    for h4_tag in li_tag.findAll('h4', attrs={'class': 'heading'}):
                        for link in h4_tag.findAll('a'):
                            if ('works' in link.get('href')) and not ('external_works' in link.get('href')):
                                work_id = link.get('href').replace('/works/', '')
                                bookmarks.append(work_id)
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

        return bookmarks

    def bookmarks(self):
        """
        Returns a list of the user's bookmarks as Work objects.

        Takes forever.

        User must be logged in to see private bookmarks.
        """

        bookmark_total = 0
        bookmark_ids = self.bookmarks_ids()
        bookmarks = []

        for bookmark_id in bookmark_ids:
            work = Work(bookmark_id, self.sess)
            bookmarks.append(work)

            bookmark_total = bookmark_total + 1
            # print (str(bookmark_total) + "\t bookmarks found.")

        return bookmarks

    def reading_history(self):
        """Returns a list of articles in the user's reading history.

        This requires the user to turn on the Viewing History feature.

        This generates a series of ``ReadingHistoryItem`` instances,
        a 2-tuple ``(work_id, last_read)``.
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
            ol_tag = soup.find('ol', attrs={'class': 'reading'})
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

                    history_items.append(ReadingHistoryItem(work_id, date))

        return history_items
