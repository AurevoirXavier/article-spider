import re
import requests

from PIL import Image
from time import time
from parsel import Selector
from tempfile import TemporaryFile
from http.cookiejar import LWPCookieJar

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
        self.__session = requests.session()
        self.__session.headers = HEADERS.copy()
        self.__session.cookies = LWPCookieJar(filename='./cookie')

    def sign_in(self, load_cookie=True, captcha=False):
        if load_cookie and self._load_cookie():
            return self.online_status()

        tokens = re.finditer(
            r"'([\w|-]+)'",
            Selector(
                self.__session.get(
                    SIGN_IN_PAGE
                ).text
            ).css('head script:nth-last-child(2)::text').extract_first()
        )

        headers = self.__session.headers.copy()
        headers.update({
            'Referer': SIGN_IN_PAGE,
            'X-Anit-Forge-Token': next(tokens).group(1),
            'X-Anit-Forge-Code': next(tokens).group(1)
        })

        if captcha:
            with TemporaryFile() as f:
                f.write(
                    self.__session.get(
                        AUTH_API.format(int(time() * 1000)),
                        headers=self.__session.headers
                    ).content
                )
                Image.open(f).show()
                f.close()

            captcha = input('Captcha: ')

            REQUEST_DATA.update({
                'request_form_verifyCode': captcha
            })

        REQUEST_DATA.update({
            'password': md5_encode('veenike' + md5_encode(LAGOU_PASSWORD) + 'veenike')
        })

        debug_online_status = self.__session.post(
            SIGN_IN_API,
            headers=headers,
            data=REQUEST_DATA
        )

        if self.online_status():
            self.__session.cookies.save()

            print('Online')
        else:
            self.sign_in(captcha=True)

    def online_status(self):
        return print(self.__session.get(
            SIGN_IN_PAGE,
            allow_redirects=False
        ).status_code == 302)

    def _load_cookie(self):
        try:
            self.__session.cookies.load(ignore_discard=True)

            return True
        except FileNotFoundError:
            return False


user = LagouUser()
user.sign_in()
