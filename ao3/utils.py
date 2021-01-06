# -*- encoding: utf-8
"""Utility functions."""

import re
from bs4 import BeautifulSoup

# Regex for extracting the work ID from an AO3 URL.  Designed to match URLs
# of the form
#
#     https://archiveofourown.org/works/1234567
#     http://archiveofourown.org/works/1234567
#
WORK_URL_REGEX = re.compile(
    r'^https?://archiveofourown.org/works/'
    r'(?P<work_id>[0-9]+)'
)


def work_id_from_url(url: str) -> str:
    """Given an AO3 URL, return the work ID."""
    match = WORK_URL_REGEX.match(url)
    if match:
        return match.group('work_id')
    else:
        raise RuntimeError('%r is not a recognised AO3 work URL')


# regex for matching href attributes in tags of the form
#   <a href="/works/28421556">...</a>
WORK_HREF_REGEX = re.compile(r'^/works/\d+$')


def work_id_from_soup(soup: BeautifulSoup) -> str:
    """
    Gets the work id from the BeautifulSoup of a fic (as given from ao3.works.iterate_pages with save_HTML=True)
    :param soup: BeautifulSoup <li> with a fic in it
    :return: the work ID as a string
    """
    a_tag = soup.find('a', {'href': WORK_HREF_REGEX})
    if a_tag is None:
        raise RuntimeError("Could not find ao3 work link in soup")

    return a_tag['href'].split('/')[2]