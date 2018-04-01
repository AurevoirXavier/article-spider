# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime

from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def default_output(value):
    return value


def date_convert(text):
    if text[0]:
        return datetime.datetime.strptime(
            re.sub(r'[ \r\n·]',
                   '',
                   text[0]
                   ),
            '%Y/%m/%d'
        )
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
    front_img_url = scrapy.Field(
        output_processor=MapCompose(default_output)
    )
    front_img_path = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    post_date = scrapy.Field(
        output_processor=MapCompose(date_convert),
    )
    category = scrapy.Field()
    tag = scrapy.Field(
        input_processor=MapCompose(tag_filter),
        output_processor=Join(',')
    )
    content = scrapy.Field()
    vote_num = scrapy.Field(
        input_processor=MapCompose(int)
    )
    bookmark_num = scrapy.Field(
        input_processor=MapCompose(num_filter)
    )
    comment_num = scrapy.Field(
        input_processor=MapCompose(num_filter)
    )
