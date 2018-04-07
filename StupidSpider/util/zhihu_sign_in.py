import re
import base64
import requests

from time import time
from http.cookiejar import LWPCookieJar
from PIL import Image

from StupidSpider.util.secret import secret
from StupidSpider.util.common import hmac_encode

SIGN_UP_ADDRESS = 'https://www.zhihu.com/signup'
SIGN_IN_ADDRESS = 'https://www.zhihu.com/api/v3/oauth/sign_in'
MULTIPART_FORM = {
    'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
    'grant_type': 'password',
    'source': 'com.zhihu.web',
    'username': '',
    'password': '',
    'lang': 'en',
    'ref_source': 'homepage'
}
HEADERS = {
    'Host': 'www.zhihu.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
    'Referer': 'https://www.zhihu.com/signup?next=%2F'
}


class ZhihuUser:
    def __init__(self):
        self.sign_up_address = SIGN_UP_ADDRESS
        self.sign_in_address = SIGN_IN_ADDRESS
        self.multipart_form = MULTIPART_FORM.copy()
        self.session = requests.session()
        self.session.headers = HEADERS.copy()
        self.session.cookies = LWPCookieJar(filename='./cookie')

    def sign_in(self, username, password, load_cookie=True):
        if load_cookie and self._load_cookie():
            return self.online_status()

        headers = self.session.headers.copy()
        timestamp = str(int(time() * 1000))

        headers.update({
            'Origin': 'https://www.zhihu.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'br, gzip, deflate',
            'Accept-Language': 'en-us',
            'DNT': '1',
            'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
            'X-Xsrftoken': self.session.get(self.sign_up_address).cookies.get('_xsrf')
        })

        self.multipart_form.update({
            'username': username,
            'password': password,
            'timestamp': timestamp,
            'signature': hmac_encode(
                self.multipart_form['grant_type'],
                self.multipart_form['client_id'],
                self.multipart_form['source'],
                timestamp
            ),
            'captcha': self._get_captcha(headers)
        })
        self.session.post(
            self.sign_in_address,
            data=self.multipart_form,
            headers=headers
        )

        return self.online_status()

    def _load_cookie(self):
        try:
            self.session.cookies.load(ignore_discard=True)

            return True
        except FileNotFoundError:
            return False

    def _get_captcha(self, headers):
        auth_address = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
        captcha = re.search(
            r'true',
            self.session.get(
                auth_address,
                headers=headers
            ).text
        )

        if captcha:
            auth = self.session.put(auth_address, headers=headers)
            base64_img = re.findall(
                r'"img_base64":"(.+)"',
                auth.text,
                re.S
            )[0].replace(r'\n', '')

            with open('captcha.jpg', 'wb') as f:
                f.write(base64.b64decode(base64_img))

            Image.open('captcha').show()

            input_text = input('Captcha: ')

            self.session.post(
                auth_address,
                data={
                    'input_text': input_text
                },
                headers=headers
            )

            return input_text
        return ''

    def online_status(self):
        if self.session.get(
                self.sign_up_address,
                allow_redirects=False
        ).status_code == 302:
            self.session.cookies.save()

            return True
        return False


user = ZhihuUser()
print(user.sign_in(secret.ZHIHU_USERNAME, secret.ZHIHU_PASSWORD))
