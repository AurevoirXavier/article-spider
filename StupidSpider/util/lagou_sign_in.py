import re
import requests

from PIL import Image
from time import time
from parsel import Selector
from tempfile import TemporaryFile

from StupidSpider.util.common import md5_encode
from StupidSpider.util.secret.secret import LAGOU_USERNAME, LAGOU_PASSWORD

SIGN_IN_PAGE = 'https://passport.lagou.com/login/login.html'
SIGN_IN_API = 'https://passport.lagou.com/login/login.json'
AUTH_API = 'https://passport.lagou.com/vcode/create?from=login&refresh={}'
HEADERS = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
}
REQUEST_DATA = {
    'username': LAGOU_USERNAME,
    'request_form_verifyCode': ''
}


class LagouUser:
    def __init__(self):
        self.__sign_in_page = SIGN_IN_PAGE
        self.__sign_in_api = SIGN_IN_API
        self.__auth_api = AUTH_API
        self.__request_data = REQUEST_DATA.copy()
        self.session = requests.session()
        self.session.headers = HEADERS.copy()

    def sign_in(self, captcha=False):
        tokens = re.finditer(
            r"'([\w|-]+)'",
            Selector(
                self.session.get(
                    self.__sign_in_page
                ).text
            ).css('head script:nth-last-child(2)::text').extract_first()
        )

        headers = self.session.headers.copy()
        headers.update({
            'Referer': self.__sign_in_page,
            'X-Anit-Forge-Token': next(tokens).group(1),
            'X-Anit-Forge-Code': next(tokens).group(1)
        })

        if captcha:
            with TemporaryFile() as f:
                f.write(
                    self.session.get(
                        self.__auth_api.format(int(time() * 1000)),
                        headers=self.session.headers
                    ).content
                )
                Image.open(f).show()
                f.close()

            captcha = input('Captcha: ')

            self.__request_data.update({
                'request_form_verifyCode': captcha
            })

        self.__request_data.update({
            'password': md5_encode('veenike' + md5_encode(LAGOU_PASSWORD) + 'veenike')
        })

        debug_online_status = self.session.post(
            self.__sign_in_api,
            headers=headers,
            data=self.__request_data
        )

        if self.online_status():
            print('Online')
        else:
            self.sign_in(captcha=True)

    def online_status(self):
        return self.session.get(
            self.__sign_in_page,
            allow_redirects=False
        ).status_code == 302


user = LagouUser()
user.sign_in()
