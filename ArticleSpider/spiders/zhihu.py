# -*- coding: utf-8 -*-
import scrapy
import re
import base64

from time import time
from ArticleSpider.util.common import hmac_encode
from PIL import Image
from ArticleSpider.util.secret.secret import ZHIHU_USERNAME, ZHIHU_PASSWORD


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    headers = {
        'Host': 'www.zhihu.com',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
        'Referer': 'https://www.zhihu.com/'
    }

    def parse(self, response):
        pass
