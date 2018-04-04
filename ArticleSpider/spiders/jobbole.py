# -*- coding: utf-8 -*-
import scrapy

from scrapy.http import Request
from urllib.parse import urljoin

from ArticleSpider.items import ArticleItemLoader, JobboleArticleItem


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item 


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')

        for post_node in post_nodes:
            front_img_url = urljoin(response.url, post_node.css('img::attr(src)').extract_first(''))
            post_url = post_node.css('::attr(href)').extract_first('')
            yield Request(
                url=urljoin(response.url, post_url),
                meta={'front_img_url': front_img_url},
                callback=self.parse_detail
            )

        next_url = response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_url:
            yield Request(url=urljoin(response.url, post_url), callback=self.parse)

    def parse_detail(self, response):
        item_loader = ArticleItemLoader(item=JobboleArticleItem(), response=response)
        item_loader.add_value('front_img_url', response.meta.get('front_img_url', ''))
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', response.url)
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_css('post_date', '.entry-meta-hide-on-mobile::text')
        item_loader.add_css('category', '.entry-meta-hide-on-mobile a[rel="category tag"]::text')
        item_loader.add_css('tag', '.entry-meta-hide-on-mobile :not([rel="category tag"])::text')
        item_loader.add_css('content', '.entry')
        item_loader.add_css('votes', '.vote-post-up h10::text')
        item_loader.add_css('bookmarks', '.bookmark-btn::text')
        item_loader.add_css('comments', 'a[href="#article-comment"] span::text')

        article_item = item_loader.load_item()

        yield article_item
