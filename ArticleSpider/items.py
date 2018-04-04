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


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class JobboleArticleItem(scrapy.Item):
    front_img_url = scrapy.Field(output_processor=Compose(list))
    front_img_path = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    post_date = scrapy.Field(output_processor=Compose(date_convert))
    category = scrapy.Field()
    tag = scrapy.Field(
        input_processor=MapCompose(lambda tag: None if '评论' in tag else tag),
        output_processor=Join(',')
    )
    content = scrapy.Field()
    votes = scrapy.Field(input_processor=MapCompose(int))
    bookmarks = scrapy.Field(input_processor=MapCompose(dot_eliminator))
    comments = scrapy.Field(input_processor=MapCompose(dot_eliminator))

    def insert_sql_with_params(self):
        insert_sql = '''
            INSERT INTO article (
                front_img_url,
                front_img_path,
                url,
                url_object_id,
                title,
                post_date,
                category,
                tag,
                content,
                votes,
                bookmarks,
                comments
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        params = (
            self['front_img_url'][0],
            self.get('front_img_path'),
            self['url'],
            self['url_object_id'],
            self['title'],
            self['post_date'],
            self['category'],
            self['tag'],
            self['content'],
            self['votes'],
            self['bookmarks'],
            self['comments']
        )

        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    question_id = scrapy.Field(input_processor=MapCompose(int))
    topics = scrapy.Field(output_processor=Join(','))
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answers = scrapy.Field()
    comments = scrapy.Field(input_processor=MapCompose(word_eliminator))
    follower = scrapy.Field()
    views = scrapy.Field()
    clicks = scrapy.Field()
    crawl_time = scrapy.Field()

    def insert_sql_with_params(self):
        insert_sql = '''
            INSERT INTO question (
                question_id,
                topics,
                url,
                title,
                content,
                answers,
                comments,
                follower,
                views,
                clicks,
                crawl_time,
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        params = (
            self['front_img_url'][0],
            self.get('front_img_path'),
            self['url'],
            self['url_object_id'],
            self['title'],
            self['post_date'],
            self['category'],
            self['tag'],
            self['content'],
            self['votes'],
            self['bookmarks'],
            self['comments']
        )

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    answer_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    votes = scrapy.Field()
    comments = scrapy.Field()
    created_time = scrapy.Field()
    updated_time = scrapy.Field()
    crawl_time = scrapy.Field()
