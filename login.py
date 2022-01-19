import os
import requests
from bs4 import BeautifulSoup


class LoginFailure(Exception):
    def __init__(self, response):
        super().__init__(f"Login failed with STATUS CODE: [{response.status_code}], possibly wrong credentials.")


class UserPageURLDetectionFailure(Exception):
    def __init__(self):
        super().__init__(
            "Unable to detect user page URL. Possible undetected login failure (Maybe human verification page)"
        )


def extract_userdata(html):
    soup = BeautifulSoup(html, 'html.parser')
    user_data_element = soup.select_one("a.my-profile")
    if user_data_element is None:
        raise UserPageURLDetectionFailure()
    else:
        return user_data_element.attrs["href"]


def get_config():
    config = {
        "email": os.environ.get("STACKOVERFLOW_EMAIL"),
        "password": os.environ.get("STACKOVERFLOW_PASSWORD")
    }
    print(config)
    return config


class StackOverflow:
    LOGIN_URL = "https://www.stackoverflow.com/users/login"
    POST_DATA_TEMPLATE = {
        "ssrc": "login"
    }

    def __init__(self, config_file="config.json"):
        self.config_file = config_file

        self.session = requests.Session()
        self.post_data = self.POST_DATA_TEMPLATE | get_config()

    def make_login_request(self):
        response = self.session.post(self.LOGIN_URL, data=self.post_data)
        if not response.ok:
            raise LoginFailure(response)
        return response

    def verify_login_success(self, user_page_url):
        full_url = "https://stackoverflow.com" + user_page_url + "?tab=votes"
        response = self.session.get(full_url)
        if not response.ok:
            raise LoginFailure(response)

    def login(self):
        response = self.make_login_request()
        user_page_url = extract_userdata(response.text)
        self.verify_login_success(user_page_url)


if __name__ == '__main__':
    stackoverflow = StackOverflow()
    stackoverflow.login()
    print("Successfully logged in!")
