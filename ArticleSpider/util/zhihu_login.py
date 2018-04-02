import requests
import re
import hmac
import base64

from time import time
from http.cookiejar import LWPCookieJar
from hashlib import sha1
from PIL import Image

HOMEPAGE = 'https://www.zhihu.com'
SIGN_IN_PAGE = 'https://www.zhihu.com/api/v3/oauth/sign_in'
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
    'Referer': 'https://www.zhihu.com/signup?next=%2F',
}


class Spider:
    def __init__(self):
        self.homepage = HOMEPAGE
        self.sign_in_page = SIGN_IN_PAGE
        self.multipart_form = MULTIPART_FORM.copy()
        self.session = requests.session()
        self.session.headers = HEADERS.copy()
        self.session.cookies = LWPCookieJar(filename='./cookie')

    def sign_in(self, username, password, load_cookie=True):
        if load_cookie and self._load_cookie():
            return self._login_status()

        headers = self.session.headers.copy()
        timestamp = str(int(time() * 1000))

        headers.update({
            'Origin': 'https://www.zhihu.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'br, gzip, deflate',
            'Accept-Language': 'en-us',
            'DNT': '1',
            'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
            'X-Xsrftoken': self._get_xsrftoken()
        })

        self.multipart_form.update({
            'username': username,
            'password': password,
            'timestamp': timestamp,
            'signature': self._get_signature(timestamp),
            'captcha': self._get_captcha(headers),
        })
        self.session.post(
            self.sign_in_page,
            data=self.multipart_form,
            headers=headers
        )

        return self._login_status()

    def _load_cookie(self):
        try:
            self.session.cookies.load(ignore_discard=True)

            return True
        except FileNotFoundError:
            return False

    def _login_status(self):
        if self.session.get(
                self.sign_in_page,
                allow_redirects=False
        ).status_code == 302:
            self.session.cookies.save()

            return True
        return False

    def _get_xsrftoken(self):
        return re.findall(
            r'_xsrf=([\w|-]+)',
            self.session
                .get(self.sign_in_page)
                .headers
                .get('Set-Cookie')
        )[0]

    def _get_signature(self, timestamp):
        signature = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=sha1)
        signature.update(
            bytes(
                MULTIPART_FORM['grant_type'] + MULTIPART_FORM['client_id'] + MULTIPART_FORM['source'] + timestamp,
                'utf8'
            )
        )

        return signature.hexdigest()

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

            with open('./captcha.jpg', 'wb') as f:
                f.write(base64.b64decode(base64_img))

            Image.open('./captcha.jpg').show()

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
