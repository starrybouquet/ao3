import requests

class AO3UserHandler():
    '''connects to User class; handles I/O'''

    self.page_urls = {'bookmarks': 'https://archiveofourown.org/users/%s/bookmarks?page=%%d',
                      'history': 'https://archiveofourown.org/users/%s/readings?page=%%d'}

    def __init__(self, user, sess=None):

        if sess == None:
            self.sess = requests.Session()
        else:
            self.sess = sess
        self.master = user

    def authenticate(username, password):

        req = self.sess.get('https://archiveofourown.org')
        soup = BeautifulSoup(req.text, features='html.parser')

        authenticity_token = soup.find('input', {'name': 'authenticity_token'})['value']

        req = self.sess.post('https://archiveofourown.org/user_sessions', params={
            'authenticity_token': authenticity_token,
            'user_session[login]': username,
            'user_session[password]': password,
        })

        # Unfortunately AO3 doesn't use HTTP status codes to communicate
        # results -- it's a 200 even if the login fails.
        if 'Please try again' in req.text:
            raise RuntimeError(
                'Error logging in to AO3; is your password correct?')
        else:
            return "Authentication successful. You are logged in."

    def get_pages(self, username, type):
        """
        Returns HTML of the user's pages of whatever type specified. Types allowed: 'bookmarks', 'history'

        User must be logged in to see private bookmarks.
        """

        api_url = (
            self.page_urls[type]
            % self.username)

        soups = [] # list of html soups saved

        for page_no in itertools.count(start=1):
            print("Finding page: \t" + str(page_no) + " of bookmarks. \t" + str(num_works) + " work ids found.")

            req = self.sess.get(api_url % page_no)
            soup = BeautifulSoup(req.text, features='html.parser')
            soups.append(soup) # append to all soups saved

            # The pagination button at the end of the page is of the form
            #
            #     <li class="next" title="next"> ... </li>
            #
            # If there's another page of results, this contains an <a> tag
            # pointing to the next page.  Otherwise, it contains a <span>
            # tag with the 'disabled' class.
            try:
                next_button = soup.find('li', attrs={'class': 'next'})
                if next_button.find('span', attrs={'class': 'disabled'}):
                    break
            except:
                # In case of absence of "next"
                break
