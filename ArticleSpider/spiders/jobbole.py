# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobboleArticleItem


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')

        for post_node in post_nodes:
            front_img_url = parse.urljoin(response.url, post_node.css('img::attr(src)').extract_first(''))
            post_url = post_node.css('::attr(href)').extract_first('')
            yield Request(
                url=parse.urljoin(response.url, post_url),
                meta={'front_img_url': front_img_url},
                callback=self.parse_detail
            )

        next_url = response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_url:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    def parse_detail(self, response):
        article_item = JobboleArticleItem()
        front_img_url = response.meta.get('front_img_url', '')
        title = response.css('.entry-header h1::text').extract_first('')
        post_date = re.sub(
            r'[ \r\n·]', '',
            response.css('.entry-meta-hide-on-mobile::text').extract_first('')
        )
        category = response.css('.entry-meta-hide-on-mobile a[rel="category tag"]::text').extract_first('')
        tag = ','.join(list(filter(
            lambda s: not s.rstrip().endswith('评论'),
            response.css('.entry-meta-hide-on-mobile :not([rel="category tag"])::text').extract()
        )))
        content = response.css('.entry').extract_first("")
        vote_num = int(response.css('.vote-post-up h10::text').extract_first(''))

        bookmark_num = response.css('.bookmark-btn::text').extract_first('')
        match_re = re.match(r'.*?(\d+).*', bookmark_num)
        if match_re:
            bookmark_num = int(match_re.group(1))
        else:
            bookmark_num = 0

        comment_num = response.css('a[href="#article-comment"] span::text').extract_first('')
        match_re = re.match(r'.*?(\d+).*', comment_num)
        if match_re:
            comment_num = int(match_re.group(1))
        else:
            comment_num = 0

        article_item['front_img_url'] = [front_img_url]
        article_item['url'] = response.url
        article_item['title'] = title
        article_item['post_date'] = post_date
        article_item['category'] = category
        article_item['tag'] = tag
        article_item['content'] = content
        article_item['vote_num'] = vote_num
        article_item['comment_num'] = comment_num
        article_item['bookmark_num'] = bookmark_num

        yield article_item
