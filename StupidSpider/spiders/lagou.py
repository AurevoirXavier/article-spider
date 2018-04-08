# -*- coding: utf-8 -*-
import re
import json
import scrapy

from PIL import Image
from time import time
from requests import get
from scrapy import Request, FormRequest
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from StupidSpider.util.secret.secret import LAGOU_USERNAME, LAGOU_PASSWORD

SIGN_IN_PAGE = 'https://passport.lagou.com/login/login.html'
SIGN_IN_API = 'https://passport.lagou.com/login/login.json'
AUTH_API = 'https://passport.lagou.com/vcode/create?from=login&refresh={}'
REFERER = 'https://passport.lagou.com/login/login.html?ts={}&serviceId=lagou&service=https%253A%252F%252Fwww.lagou.com%252F&action=login&signature=3DD28DEA42F297A5EDFCFDF1A962AE87C1'
HEADERS = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
}
UPDATE_HEADERS = {
    'Host': 'www.lagou.com',
    'Referer': 'https://www.lagou.com/'
}
REQUEST_DATA = {
    'username': LAGOU_USERNAME,
    'password': LAGOU_PASSWORD,
    'request_form_verifyCode': ''
}


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=('zhaopin/.*', )), follow=True),
        Rule(LinkExtractor(allow=('gongsi/\d+.html', )), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_item', follow=True)
    )

    sign_in_page = SIGN_IN_PAGE
    sign_in_api = SIGN_IN_API
    referer = REFERER
    auth_api = AUTH_API
    request_data = REQUEST_DATA.copy()
    headers = HEADERS.copy()

    def start_requests(self, auth={}):
        return [Request(self.sign_in_page, headers=self.headers, meta=auth, callback=self._sign_in)]

    def _sign_in(self, response):
        tokens = re.finditer(
            r"'([\w|-]+)'",
            response.css('head script:nth-last-child(2)::text').extract_first()
        )
        timestamp = str(int(time() * 1000))
        headers = self.headers.copy()

        headers.update({
            'Referer': self.referer.format(timestamp),
            'X-Anit-Forge-Token': next(tokens).group(1),
            'X-Anit-Forge-Code': next(tokens).group(1)
        })

        if response.meta.get('auth'):
            with open('./util/captcha', 'wb') as f:
                f.write(
                    get(
                        self.auth_api.format(timestamp),
                        headers=headers
                    ).content
                )

            Image.open('./util/captcha').show()

            captcha = input('Captcha: ')

            self.request_data.update({
                'request_form_verifyCode': captcha
            })

        return [FormRequest(
            url=self.sign_in_api,
            headers=headers,
            formdata=self.request_data,
            callback=self._online_status,
            dont_filter=True
        )]

    def _online_status(self, response):
        if json.loads(response.text)['message'] == '操作成功':
            self.headers.update(UPDATE_HEADERS)

            for url in self.start_urls:
                yield Request(url, headers=self.headers, dont_filter=True)
        else:
            self.start_requests(
                auth={
                    'auth': True
                }
            )

    def parse_item(self, response):
        i = {}
        # i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        # i['name'] = response.xpath('//div[@id="name"]').extract()
        # i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
