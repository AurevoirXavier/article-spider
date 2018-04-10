# -*- coding: utf-8 -*-
import re
import scrapy

from datetime import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from StupidSpider.items import LagouJobItem, LagouJobItemLoader
from StupidSpider.util.secret.secret import LAGOU_COOKIES


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=r'zhaopin/.*'), follow=True),
        Rule(LinkExtractor(allow=r'gongsi/\d+.html'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True)
    )

    custom_settings = {
        "COOKIES_ENABLED": False,
        'DEFAULT_REQUEST_HEADERS': {
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
            'Connection': 'keep-alive',
            'Cookie': LAGOU_COOKIES
        }
    }

    def parse_job(self, response):
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_value('url', response.url)
        item_loader.add_css('position', '.job-name::attr(title)')
        item_loader.add_css('salary', '.salary::text')
        item_loader.add_css('city', '.job_request p>:nth-child(2)::text')
        item_loader.add_css('experience', '.job_request p>:nth-child(3)::text')
        item_loader.add_css('degree_require', '.job_request p>:nth-child(4)::text')
        item_loader.add_css('type', '.job_request p>:nth-child(5)::text')
        item_loader.add_css('label', '.position-label li::text')
        item_loader.add_css('publish_time', '.publish_time::text')
        item_loader.add_css('advantage', '.job-advantage p::text')
        item_loader.add_css('description', '.job_bt div')
        item_loader.add_value(
            'address',
            '-'.join(
                response.css('.work_addr a::text').extract()[:-1]
                +
                [re.sub(r'\n|-| ', '', response.css('.work_addr::text').extract()[-2])])
        )
        item_loader.add_css('company_name', '#job_company dt a img::attr(alt)')
        item_loader.add_css('company_page', '#job_company dt a::attr(href)')
        item_loader.add_value('crawl_time', datetime.now())

        a = item_loader.load_item()
        return item_loader.load_item()
