# -*- encoding: utf-8

import requests
import getpass
import json
import urllib.parse

from bs4 import BeautifulSoup

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

    # USER METHODS

    def login(self, username):
        """Log in to the archive.

        This allows you to access pages that are only available while
        logged in.  This doesn't do any checking that the password is correct.

        """
        password = getpass.getpass('Password: ')
        self.user = User(username=username, handler=self.handler)
        print(self.handler.login(username, password))

    def get_user(self):
        """Get the user object connected to this instance.
        """
        return self.user

    # WORK METHODS

    def work(self, id):
        """Look up a work that's been posted to AO3.

        :param id: the work ID.  In the URL to a work, this is the number.
            e.g. the work ID of http://archiveofourown.org/works/1234 is 1234.
        """
        return Work(id=id, io_handler=self.handler)

    def tag(self, tag_name, load=False, save_while_loading=True, filename_template="html/{0}_html_{1}.txt", pageRange=(None,None)):
        """Get all works within a searchable tag on AO3.
        Returns a tuple (ids, soups)
        where ids is a list of all work IDs and soups is a list of all soups for that work
        If load=True, loads all works so that a list of works are returned in the tuple
            instead of a list of soups"""
        converted_tag = urllib.parse.quote(tag_name).replace('/', '*s*')
        pages = self.handler.get_pages('', 'tags', tag=converted_tag, save_while_loading=save_while_loading, filename_template=filename_template, pageRange=pageRange)
        soups = iterate_pages(pages, 'work', saveHTML=True)
        if load == True:
            works = [Work(id=id, io_handler=self.handler, load=False, soup=soup) for soup in soups]
            return (soups, works)
        else:
            return soups

    def load_from_html(self, filename=None, filename_template=None, file_num_end=0, file_num_start=0):
        """Load works from saved HTML of AO3 pages."""
        soups = []
        if filename:
            with open(filename, 'r') as f:
                html = f.read()
                soups.append(BeautifulSoup(html, 'html.parser'))
        elif filename_template:
            for n in range(file_num_start, file_num_end+1):
                with open(filename_template.format(n), 'r') as f:
                    html = f.read()
                    soups.append(BeautifulSoup(html, 'html.parser'))
        print("Loaded soups. Getting works.")

        all_works_html = iterate_pages(soups, 'work', save_HTML=True)

        all_works = []
        for id, work in all_works_html.items():
            work_item = Work(id, self.handler, load=False, soup=work)
            all_works.append(work_item)

        return all_works

    def to_json(self, works, filename):
        """Convert list of Work objects to a json file."""

        json_data = {}

        for work in works:
            print('Writing work with id {}'.format(work.id))
            item = work.json()
            json_data[work.id] = item

        with open(filename, 'w') as f:
            json.dump(json_data, f)

        return filename


class WorkNotFound(Exception):
    pass


class RestrictedWork(Exception):
    pass