# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/']

    def parse(self, response):
        post_urls = response.css('#archive .floated-thumb .post-thumb a::attr(href)').extract()
        for post_url in post_urls:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_detail)

    def parse_detail(self, response):
        title = response.css('.entry-header h1::text').extract_first("")
        post_date = re.sub(
            r'[ \r\n·]', '',
            response.css('.entry-meta-hide-on-mobile::text').extract_first("")
        )
        tag = ','.join(list(filter(
            lambda s: not s.rstrip().endswith('评论'),
            response.css('.entry-meta-hide-on-mobile a::text').extract()
        )))
        content = response.css('.entry').extract_first("")
        vote_num = int(response.css('.vote-post-up h10::text').extract_first(""))

        bookmark_num = response.css('.bookmark-btn::text').extract_first("")
        match_re = re.match(r'.*?(\d+).*', bookmark_num)
        if match_re:
            bookmark_num = int(match_re.group(1))

        comment_num = response.css('a[href="#article-comment"] span::text').extract_first("")
        match_re = re.match(r'.*?(\d+).*', comment_num)
        if match_re:
            comment_num = int(match_re.group(1))

        pass
