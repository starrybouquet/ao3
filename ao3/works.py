# -*- encoding: utf-8

from datetime import datetime
import json

from bs4 import BeautifulSoup, Tag

from .handlers import AO3Handler

def iterate_pages(page_soups, class_name, save_HTML=False):
    """Iterate over pages of lists of works.
    Options for class_name: 'bookmark'
                            'work'
    """
    if save_HTML:
        works = {}
    ids = []
    num_works = 0
    page_no = 0

    for page in page_soups:
        page_no += 1
        print("Inspecting page: \t" + str(page_no) + " of list. \t" + str(num_works) + " work ids found.")

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
        try:
            ol_tag = page.find('ol', attrs={'class': class_name})
        except Exception as e:
            print(ol_tag)
            return e


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
                            ids.append(work_id)
                if save_HTML:
                    works[work_id] = li_tag

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

    if save_HTML:
        return works
    else:
        return ids

class Work(object):
    """Short summary.

    Parameters
    ----------
    id : str
        Work id.
    [io_handler] : AO3PublicHandler object; default None
        Public handler for accessing data of work.
    [load] : bool; default True
        If true, loads work data using I/O handler on init.
        Otherwise, does not load until load_data is called explicitly.
        This allows for full separation of I/O and parsing.
    [soup] : BeautifulSoup object; default None
        If not None, uses this html rather than loading its own data.

    Attributes
    ----------
    _io_handler : AO3Handler
        Public handler for accessing work data.
    _html : str
        HTML of work in string form
    _soup : BeautifulSoup object
        HTML soup of work in BeautifulSoup form.
    id : str
        work id

    """

    def __init__(self, id, io_handler, load=True, soup=None):
        self.id = id

        self._io_handler = io_handler

        self.id = id

        if load == True:
            self.load_data()
        elif soup != None:
            self._soup = soup
            self._html = str(self._soup)
            self._source = 'search'
        else:
            self._html = 'HTML not loaded. Please call load_data() function.'
            self._soup = BeautifulSoup('Nothing here...', 'html.parser')
            self._source = 'none'

    def __repr__(self):
        return '%s(id=%r)' % (type(self).__name__, self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(repr(self))

    def load_data(self):
        """Load data using I/O handler"""
        try:
            self._html = self._io_handler.get_work_soup(self.id)
            self._soup = BeautifulSoup(self._html, 'html.parser')
            self._source = 'work'
            return 'Work loaded'
        except Exception as e: # if exception occurs, data was not loaded properly
            print('Work could not be loaded.')
            raise e

    @property
    def url(self):
        """A URL to this work."""
        return 'https://archiveofourown.org/works/%s' % self.id

    @property
    def title(self):
        """The title of this work."""
        if self._source == 'work':
        # The title of the work is stored in an <h2> tag of the form
        #
        #     <h2 class="title heading">[title]</h2>
        #
        # TODO: Retrieve title from restricted work
            title_tag = self._soup.find('h2', attrs={'class': 'title'})
            return title_tag.contents[0].strip()
        elif self._source == 'search':
            heading_tag = self._soup.find('h4', attrs={'class': 'heading'})
            return heading_tag.find_all('a')[0].get_text().strip()

    @property
    def author(self):
        """The author of this work."""
        if self._source == 'work':
            # The author of the work is kept in the byline, in the form
            #
            #     <h3 class="byline heading">
            #       <a href="/users/[author_name]" rel="author">[author_name]</a>
            #     </h3>
            #
            byline_tag = self._soup.find('h3', attrs={'class': 'byline'})
            a_tag = [t
                     for t in byline_tag.contents
                     if isinstance(t, Tag)]
            assert len(a_tag) == 1
            return a_tag[0].contents[0].strip()
        elif self._source == 'search':
            heading_tag = self._soup.find('h4', attrs={'class': 'heading'})
            if 'archived by' in heading_tag.get_text():
                author_and_archive = heading_tag.get_text().partition('by ')[2]
                return author_and_archive.partition(' [')[0].strip()
            headers = heading_tag.find_all('a')
            if len(headers) > 1:
                return headers[1].get_text().strip()
            else:
                return 'Anonymous'

    @property
    def summary(self):
        """The author summary of the work."""
        # The author summary is kept in the following format:
        #
        #     <div class="summary module" role="complementary">
        #       <h3 class="heading">Summary:</h3>
        #       <blockquote class="userstuff">
        #         [author_summary_html]
        #       </blockquote>
        #     </div>
        #
        if self._source == 'work':
            summary_div = self._soup.find('div', attrs={'class': 'summary'})
            blockquote = summary_div.find('blockquote')
        elif self._source == 'search':
            blockquote = self._soup.find('blockquote', attrs={'class': 'summary'})
        if blockquote != None:
            return blockquote.renderContents().decode('utf8').strip()
        else: # blockquote will throw an error if author put no summary so just return none instead
            return ''

    def _lookup_stat(self, class_name, default=None, linked=False):
        """Returns the value of a stat."""
        # The stats are stored in a series of divs of the form
        #
        #     <dd class="[field_name]">[field_value]</div>
        #
        # This is a convenience method for looking up values from these divs.
        #
        dd_tag = self._soup.find('dd', attrs={'class': class_name})
        if dd_tag is None:
            return default
        if 'tags' in dd_tag.attrs['class']:
            return self._lookup_list_stat(dd_tag=dd_tag)
        if linked:
            # return dd_tag.a.contents[0].strip("\n").strip()
            return dd_tag.a.contents[0].strip()
        else:
            # return dd_tag.contents[0].strip("\n").strip()
            return dd_tag.contents[0].strip()

    def _lookup_list_stat(self, dd_tag):
        """Returns the value of a list statistic.

        Some statistics can have multiple values (e.g. the list of characters).
        This helper method should be used to retrieve those.

        """
        # A list tag is stored in the form
        #
        #     <dd class="[field_name] tags">
        #       <ul class="commas">
        #         <li><a href="/further-works">[value 1]</a></li>
        #         <li><a href="/more-info">[value 2]</a></li>
        #         <li class="last"><a href="/more-works">[value 3]</a></li>
        #       </ul>
        #     </dd>
        #
        # We want to get the data from the individual <li> elements.
        li_tags = dd_tag.findAll('li')
        a_tags = [t.contents[0] for t in li_tags]
        return [t.contents[0] for t in a_tags]

    def _lookup_stat_icon(self, icon_class):
        icon_span = self._soup.find('span', attrs={'class': icon_class})
        return [t.strip() for t in icon_span['title'].split(',')]

    @property
    def rating(self):
        """The age rating for this work."""
        if self._source == 'work':
            return self._lookup_stat('rating', [])
        elif self._source == 'search':
            return self._lookup_stat_icon('rating')

    @property
    def warnings(self):
        """Any archive warnings on the work."""
        if self._source == 'work':
            value = self._lookup_stat('warning', [])
        elif self._source == 'search':
            value = self._lookup_stat_icon('warnings')
        if value == ['No Archive Warnings Apply']:
            return []
        else:
            return value

    @property
    def category(self):
        """The category of the work."""
        if self._source == 'work':
            return self._lookup_stat('category', [])
        elif self._source == 'search':
            return self._lookup_stat_icon('category')

    @property
    def fandoms(self):
        """The fandoms in this work."""
        if self._source == 'work':
            return self._lookup_stat('fandom', [])
        elif self._source == 'search':
            fandom_tag = self._soup.find('h5', attrs={'class': 'fandoms'})
            return fandom_tag.a.get_text().strip()

    @property
    def relationship(self):
        """The relationships in this work."""
        return self._lookup_stat('relationship', [])

    @property
    def characters(self):
        """The characters in this work."""
        return self._lookup_stat('character', [])

    @property
    def additional_tags(self):
        """Any additional tags on the work."""
        return self._lookup_stat('freeform', [])

    @property
    def language(self):
        """The language in which this work is published."""
        return self._lookup_stat('language', "").strip()

    @property
    def published(self):
        """The date when this work was published."""
        if self._source == 'work':
            date_str = self._lookup_stat('published')
            date_val = datetime.strptime(date_str, '%Y-%m-%d')
        elif self._source == 'search':
            date_str = self._soup.find('p', attrs={'class': 'datetime'}).get_text().strip()
            date_val = datetime.strptime(date_str, '%d %b %Y')
        return date_val.date()

    @property
    def words(self):
        """The number of words in this work."""
        return int(self._lookup_stat('words', 0).replace(',',''))

    @property
    def chapters_posted(self):
        """The number of chapters posted."""
        # try:
        #     text = self._lookup_stat('chapters', default='1/1')
        #     # print()
        #     # print(text)
        #     if text == '':
        #         # print('Text was empty, trying link')
        #         text = self._lookup_stat('chapters', default='1/1', linked=True)
        #         return int(text)
        #
        #     # print('Chapter full text: {}'.format(text))
        #     return int(text.split('/')[0])
        # except Exception as e:
        #     print('Error: {}'.format(e))
        #     print('Chapter tag contents looks like: {}'.format(text))
        #     x = str(input('Chapters posted cannot be found. Hit s to skip, q to break'))
        #     if x == 'q':
        #         raise e
        #     elif x == 's':
        #         return '1'

        try:
            chapters_tag_contents = self._soup.find('dd', attrs={'class': 'chapters'}).contents
            if chapters_tag_contents[0] == '\n':
                chapters = chapters_tag_contents[2].partition('/')[0]
            elif '1/' in chapters_tag_contents[0]:
                chapters = '1'
            else:
                chapters = chapters_tag_contents[0].get_text()

            if (chapters.isdigit() == True) or (chapters == '?'):
                return chapters
            else:
                print('Chapter was not a number or ?. Tag contents are as follows')
                print(chapters_tag_contents)
                x = str(input('Enter a value, or enter s to skip and return ?'))
                if x == 's':
                    return '?'
                else:
                    return x
        except Exception as e:
            print('Error: {}'.format(e))
            print('Chapter tag contents looks like: {}'.format(chapters_tag_contents))
            x = str(input('Chapters posted cannot be found. Hit s to return default value ?, q to break, e to enter value'))
            if x == 'q':
                raise e
            elif x == 's':
                return '?'
            elif x == 'e':
                return int(input('enter value: '))

    @property
    def chapters_total(self):
        try:
            chapters_tag_contents = self._soup.find('dd', attrs={'class': 'chapters'}).contents
            if chapters_tag_contents[0] == '\n':
                total_chapters = chapters_tag_contents[2].partition('/')[2]
            elif '1/' in chapters_tag_contents[0]:
                total_chapters = '1'
            else:
                total_chapters = chapters_tag_contents[1].partition('/')[2]

            if (total_chapters.isdigit() == True) or (total_chapters == '?'):
                return total_chapters
            else:
                print('Chapter was not a number or ?. tag contents are as follows')
                print(chapters_tag_contents)
                x = str(input('Enter a value, or enter s to skip and return ?'))
                if x == 's':
                    return '?'
                else:
                    return x

        except Exception as e:
            print('Error: {}'.format(e))
            print('Chapter tag contents looks like: {}'.format(chapters_tag_contents))
            x = str(input('Chapters total cannot be found. Hit s to skip, q to break, e to enter value.'))
            if x == 'q':
                raise e
            elif x == 's':
                return '?'
            elif x == 'e':
                return int(input('enter value: '))

    @property
    def comments(self):
        """The number of comments on this work."""
        if self._source == "work":
            return int(self._lookup_stat('comments', default='0').replace(',',''))
        elif self._source == "search":
            return int(self._lookup_stat('comments', default='0', linked=True).replace(',',''))


    @property
    def kudos(self):
        """The number of kudos on this work."""
        if self._source == "work":
            return int(self._lookup_stat('kudos', default='0').replace(',',''))
        elif self._source == "search":
            return int(self._lookup_stat('kudos', default='0', linked=True).replace(',',''))

    @property
    def complete(self):
        """Returns True if posted chapters = total chapters, False if not"""
        return (str(self.posted_chapters) == str(self.total_chapters))

    @property
    def kudos_left_by(self):
        """Returns a list of usernames who left kudos on this work.
        requires work to be loaded, as the kudos left are not available on the search result"""
        # The list of usernames who left kudos is stored in the following
        # format:
        #
        #     <div id="kudos">
        #       <p class="kudos">
        #         <a href="/users/[username1]">[username1]</a>
        #         <a href="/users/[username2]">[username2]</a>
        #         ...
        #       </p>
        #     </div>
        #
        # And yes, this really does include every username.  The fic with the
        # most kudos is http://archiveofourown.org/works/2080878, and this
        # approach successfully retrieved the username of everybody who
        # left kudos.
        if self._source == 'search':
            self.load_data()

        kudos_div = self._soup.find('div', attrs={'id': 'kudos'})
        for a_tag in kudos_div.findAll('a'):

            # If a fic has lots of kudos, not all the users who left kudos
            # are displayed by default.  There's a link for expanding the
            # list of users:
            #
            #     <a href="/works/[work_id]/kudos" id="kudos_summary">
            #
            # and another for collapsing the list afterward:
            #
            #     <a href="#" id="kudos_collapser">
            #
            if a_tag.attrs.get('id') in ('kudos_collapser', 'kudos_summary'):
                continue

            # There's sometimes a kudos summary that can be expanded to

            yield a_tag.attrs['href'].replace('/users/', '')

    @property
    def bookmarks(self):
        """The number of times this work has been bookmarked."""
        # This returns a link of the form
        #
        #     <a href="/works/9079264/bookmarks">102</a>
        #
        # It might be nice to follow that page and get a list of who has
        # bookmarked this, but for now just return the number.
        return int(self._lookup_stat('bookmarks', 0, True))

    @property
    def hits(self):
        """The number of hits this work has received."""
        return int(self._lookup_stat('hits', 0))

    def json(self, *args, **kwargs):
        """Provide a complete representation of the work in JSON.

        *args and **kwargs are passed directly to `json.dumps()` from the
        standard library.

        """
        data = {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'summary': self.summary,
            'rating': self.rating,
            'warnings': self.warnings,
            'category': self.category,
            'fandoms': self.fandoms,
            'relationship': self.relationship,
            'characters': self.characters,
            'additional_tags': self.additional_tags,
            'language': self.language,
            'stats': {
                'published': str(self.published),
                'words': self.words,
                'chapters posted': self.chapters_posted,
                'chapters total': self.chapters_total,
                'comments': self.comments,
                'kudos': self.kudos,
                'bookmarks': self.bookmarks,
                'hits': self.hits,
            }
        }
        return json.dumps(data, *args, **kwargs)

    # def csv(self):
    #     """Provides a complete representation of the work as a csv row format.
    #     Intended to be combined with other works
    #     for example, a tag could be represented in a csv table.
    #     columns would be the titles shown in the json() function.
    #     """
    #     try:
    #         data = [self.id, self.title, self.author, self.summary,
    #                 self.rating, self.warnings, self.category,
    #                 self.fandoms, self.relationship, self.characters, self.additional_tags,
    #                 self.language, self.published, self.words, self.chapters_posted, self.chapters_total,
    #                 self.comments, self.kudos, self.bookmarks, self.hits]
    #         return ', '.join(['"{0}"'.format(str(item)) for item in data])
    #     except Exception as e:
    #         print('Exception while getting data of work with id {}.'.format(self.id))
    #         raise e
