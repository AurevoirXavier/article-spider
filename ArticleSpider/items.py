# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime

from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, MapCompose, TakeFirst, Join

from ArticleSpider.util.common import md5_encode


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(text):
    date = re.sub(r'[ \r\n·]', '', text[0])
    if date:
        return datetime.datetime.strptime(date, '%Y/%m/%d')
    else:
        return datetime.datetime.now()


def num_filter(text):
    match_re = re.match(r'.*?(\d+).*', text)
    if match_re:
        return int(match_re.group(1))
    else:
        return 0


def tag_filter(tag):
    if '评论' in tag:
        return None
    else:
        return tag


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class JobboleArticleItem(scrapy.Item):
    front_img_url = scrapy.Field(output_processor=Compose(list))
    front_img_path = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field(input_processor=MapCompose(md5_encode))
    title = scrapy.Field()
    post_date = scrapy.Field(output_processor=Compose(date_convert))
    category = scrapy.Field()
    tag = scrapy.Field(
        input_processor=MapCompose(tag_filter),
        output_processor=Join(',')
    )
    content = scrapy.Field()
    vote_num = scrapy.Field(input_processor=MapCompose(int))
    bookmark_num = scrapy.Field(input_processor=MapCompose(num_filter))
    comment_num = scrapy.Field(input_processor=MapCompose(num_filter))
