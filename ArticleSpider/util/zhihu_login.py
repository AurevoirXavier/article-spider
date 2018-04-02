import requests
import re
import http.cookiejar

from scrapy import Selector

session = requests.session()
session.headers = {
    'Origin': 'https://www.zhihu.com',
    'Host': 'www.zhihu.com',
    'Accept': 'application/json, text/plain, */*',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'br, gzip, deflate',
    'Accept-Language': 'en-us',
    'DNT': '1',
    'Authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
    'Referer': 'https://www.zhihu.com/signup?next=%2F'
}


def header_generator():
    response = Selector(session
                        .get('https://www.zhihu.com/')
                        .text
                        )

    response.css()


def login(account, password):
    url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
    header = None  # TODO
