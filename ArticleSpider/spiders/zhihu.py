# -*- coding: utf-8 -*-
import scrapy
import re
import base64

from time import time
from ArticleSpider.util.common import hmac_encode
from PIL import Image
from ArticleSpider.util.secret.secret import ZHIHU_USERNAME, ZHIHU_PASSWORD

SIGN_UP_ADDRESS = 'https://www.zhihu.com/signup'
SIGN_IN_ADDRESS = 'https://www.zhihu.com/api/v3/oauth/sign_in'
AUTH_ADDRESS = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
HEADERS = {
    'Host': 'www.zhihu.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
    'Referer': 'https://www.zhihu.com/'
}
FORM_DATA = {
    'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
    'grant_type': 'password',
    'source': 'com.zhihu.web',
    'username': '',
    'password': '',
    'lang': 'en',
    'ref_source': 'homepage'
}


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    sign_up_address = SIGN_UP_ADDRESS
    sign_in_address = SIGN_IN_ADDRESS
    auth_address = AUTH_ADDRESS
    headers = HEADERS.copy()
    form_data = FORM_DATA.copy()

    def start_requests(self):
        return [scrapy.Request(self.sign_up_address, headers=self.headers, callback=self._sign_in)]

    def _sign_in(self, response):
        headers = self.headers.copy()
        headers.update({
            'Origin': 'https://www.zhihu.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'br, gzip, deflate',
            'Accept-Language': 'en-us',
            'DNT': '1',
            'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
            'X-Xsrftoken': re.search(
                r'_xsrf=([\w|-]+)',
                response.headers.getlist(b'Set-Cookie')[1].decode('utf8')
            ).group(1)
        })

        timestamp = str(int(time() * 1000))
        self.form_data.update({
            'username': ZHIHU_USERNAME,
            'password': ZHIHU_PASSWORD,
            'timestamp': timestamp,
            'signature': hmac_encode(
                self.form_data['grant_type'],
                self.form_data['client_id'],
                self.form_data['source'],
                timestamp
            ),
            'captcha': ''
        })

        yield scrapy.Request(
            self.auth_address,
            headers=headers,
            meta={
                'headers': headers,
                'form_data': self.form_data
            },
            callback=self._auth
        )

    def _auth(self, response):
        headers = response.meta.get('headers')

        if re.search(r'true', response.text):
            yield scrapy.Request(
                self.auth_address,
                method='PUT',
                headers=headers,
                meta={
                    'headers': headers,
                    'form_data': self.form_data
                }
                , callback=self._get_captcha)
        else:
            yield scrapy.FormRequest(
                url=self.sign_in_address,
                headers=headers,
                formdata=response.meta.get('form_data'),
                callback=self._online_status
            )

    def _get_captcha(self, response):
        headers = response.meta.get('headers')
        form_data = response.meta.get('form_data')
        base64_img = re.findall(
            r'"img_base64":"(.+)"',
            response.text,
            re.S
        )[0].replace(r'\n', '')

        with open('./util/captcha', 'wb') as f:
            f.write(base64.b64decode(base64_img))

        Image.open('./util/captcha').show()

        input_text = input('Captcha: ')

        scrapy.FormRequest(
            url=self.auth_address,
            headers=headers,
            formdata={
                'input_text': input_text
            },
            meta=response.meta,
        )

        form_data.update({
            'captcha': input_text
        })

        yield scrapy.FormRequest(
            url=self.sign_in_address,
            headers=headers,
            formdata=form_data,
            callback=self._online_status
        )

    def _online_status(self, response):
        if response.status == 201:
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)

    def parse(self, response):
        pass
