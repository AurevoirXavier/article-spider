# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime

from scrapy.loader.processors import MapCompose, TakeFirst


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(date):
    date = re.sub(r'[ \r\n·]', '', date)

    if date:
        return datetime.datetime.strptime(date, '%Y/%m/%d')
    else:
        return None


class JobboleArticleItem(scrapy.Item):
    front_img_url = scrapy.Field()
    front_img_path = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field(
        # input_processor=MapCompose(lambda x: x + '-xavier')
    )
    post_date = scrapy.Field(
        input_processor=MapCompose(date_convert),
        output_processor=TakeFirst()
    )
    category = scrapy.Field()
    tag = scrapy.Field()
    content = scrapy.Field()
    vote_num = scrapy.Field()
    bookmark_num = scrapy.Field()
    comment_num = scrapy.Field()
