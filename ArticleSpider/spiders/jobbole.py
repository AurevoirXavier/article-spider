# -*- coding: utf-8 -*-
import scrapy
import re


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/110287/']

    def parse(self, response):
        title = response.xpath('//div[@class["entry-header"]/h1/text()')
        create_date = re.sub(
            r'[ \r\n·]', '',
            response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0]
        )
        tag = ','.join(list(filter(
            lambda s: not s.rstrip().endswith('评论'),
            response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        )))
        content = response.xpath('//div[@class="entry"]').extract()[0]
        praise_num = int(response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract()[0])

        fav_num = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract()[0]
        match_re = re.match(r'.*(\d+).*', fav_num)
        if match_re:
            fav_num = match_re.group(1)

        comment_num = response.xpath('//a[@href="#article-comment"]/text()').extract()[0]
        match_re = re.match(r'.*(\d+).*', comment_num)
        if match_re:
            fav_num = match_re.group(1)

        pass
