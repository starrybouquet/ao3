# -*- encoding: utf-8

import requests
import getpass
import urllib.parse

from .utils import *
from .users import User
from .works import Work, iterate_pages
from .handlers import AO3Handler

class AO3(object):
    """A scraper for the Archive of Our Own (AO3)."""

    def __init__(self):
        self.user = None
        self.handler = AO3Handler(self)

    def __repr__(self):
        return '%s()' % (type(self).__name__)

    # WORK METHODS

    def work(self, id):
        """Look up a work that's been posted to AO3.

        :param id: the work ID.  In the URL to a work, this is the number.
            e.g. the work ID of http://archiveofourown.org/works/1234 is 1234.
        """
        return Work(id=id, io_handler=self.handler)

    def tag(self, tag_name, load=False): # CURRENTLY DEAD
        """Get all works within a searchable tag on AO3.
        Returns a tuple (ids, soups)
        where ids is a list of all work IDs and soups is a list of all soups for that work
        If load=True, loads all works so that a list of works are returned in the tuple
            instead of a list of soups"""
        converted_tag = urllib.parse.quote(tag_name).replace('/', '*s*')
        pages = self.handler.get_pages('', 'tags', tag=converted_tag)
        soups = iterate_pages(pages, 'work', saveHTML=True)
        if load == True:
            works = [Work(id=id, io_handler=self.handler, load=False, soup=soup) for soup in soups]
            return (soups, works)
        else:
            return soups

    def to_csv(self, works, filename):
        """Convert list of Work objects to a csv file."""

        with open(filename, 'w') as f:
            columns = ['id', 'title', 'author', 'summary',
            'rating', 'warnings', 'category', 'fandoms', 'relationship', 'characters', 'additional_tags',
            'language', 'published', 'words', 'chapters_posted', 'chapters_total',
            'comments', 'kudos', 'bookmarks', 'hits']
            f.write(', '.join([c for c in columns]))
            f.write('\n')
            for work in works:
                print('Writing work with id {}'.format(work.id))
                csv_line = work.csv() + '\n'
                f.write(csv_line)

        return filename

    # USER METHODS

    def login(self, username):
        """Log in to the archive.

        This allows you to access pages that are only available while
        logged in.  This doesn't do any checking that the password is correct.

        """
        password = getpass.getpass('Password: ')
        self.user = User(username=username, handler=self.handler)
        print(self.handler.login(username, password))
