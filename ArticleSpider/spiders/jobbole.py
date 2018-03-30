# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        post_urls = response.css('#archive .floated-thumb .post-thumb a::attr(href)').extract()

        for post_url in post_urls:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_detail)

        next_url = response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_url:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    def parse_detail(self, response):
        title = response.css('.entry-header h1::text').extract_first("")
        post_date = re.sub(
            r'[ \r\n·]', '',
            response.css('.entry-meta-hide-on-mobile::text').extract_first("")
        )
        category_tag = response.css('.entry-meta-hide-on-mobile a::text').extract()
        category = category_tag[0]
        tag = category_tag[-1]
        content = response.css('.entry').extract_first("")
        vote_num = int(response.css('.vote-post-up h10::text').extract_first(""))

        bookmark_num = response.css('.bookmark-btn::text').extract_first("")
        match_re = re.match(r'.*?(\d+).*', bookmark_num)
        if match_re:
            bookmark_num = int(match_re.group(1))
        else:
            bookmark_num = 0

        comment_num = response.css('a[href="#article-comment"] span::text').extract_first("")
        match_re = re.match(r'.*?(\d+).*', comment_num)
        if match_re:
            comment_num = int(match_re.group(1))
        else:
            comment_num = 0

        pass
