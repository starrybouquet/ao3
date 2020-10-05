# -*- encoding: utf-8

import requests

from utils import *
from users import User
from works import Work, iterate_pages
from handlers import AO3Handler

class AO3(object):
    """A scraper for the Archive of Our Own (AO3)."""

    def __init__(self):
        self.user = None
        self.handler = AO3Handler(self)

    def __repr__(self):
        return '%s()' % (type(self).__name__)

    def work(self, id):
        """Look up a work that's been posted to AO3.

        :param id: the work ID.  In the URL to a work, this is the number.
            e.g. the work ID of http://archiveofourown.org/works/1234 is 1234.
        """
        return Work(id=id, io_handler=self.handler)

    def tag(self, tag_name, load=False):
        """Get all works within a searchable tag on AO3.
        Returns a tuple (ids, soups)
        where ids is a list of all work IDs and soups is a list of all soups for that work
        If load=True, loads all works so that a list of works are returned in the tuple
            instead of a list of soups"""
        converted_tag = tag_name # TODO: CHANGE TO FIX PERCENT ENCODING ISSUES
        pages = self.handler.get_pages(converted_tag, 'tags')
        (ids, soups) = iterate_pages(pages)
        if load == True:
            works = [Work(id=id, io_handler=self.handler, load=False, soup=soup) for soup in soups]
            return (ids, works)
        else:
            return (ids, soups)

    def login(self, username, password):
        """Log in to the archive.

        This allows you to access pages that are only available while
        logged in.  This doesn't do any checking that the password is correct.

        """
        self.user = User(username=username, handler=self.handler)
        self.handler.login(username, password)
