# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, MapCompose, TakeFirst, Join
from util import common


class StupidspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class JobboleArticleItem(scrapy.Item):
    front_img_url = scrapy.Field(output_processor=Compose(list))
    front_img_path = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    post_date = scrapy.Field(output_processor=Compose(common.date_convert))
    category = scrapy.Field()
    tag = scrapy.Field(
        input_processor=MapCompose(lambda tag: None if '评论' in tag else tag),
        output_processor=Join(',')
    )
    content = scrapy.Field()
    votes = scrapy.Field(input_processor=MapCompose(int))
    bookmarks = scrapy.Field(input_processor=MapCompose(common.jobbole_dot_eliminator))
    comments = scrapy.Field(input_processor=MapCompose(common.jobbole_dot_eliminator))

    def insert_sql_with_params(self):
        insert_sql = '''
            INSERT INTO jobbole_spider.article (
                front_img_url,
                front_img_path,
                url,
                url_id,
                title,
                post_date,
                category,
                tag,
                content,
                votes,
                bookmarks,
                comments
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url_id) DO UPDATE
                SET votes = excluded.votes,
                    bookmarks = excluded.bookmarks,
                    comments = excluded.comments
            '''
        params = (
            self['front_img_url'][0],
            self.get('front_img_path'),
            self['url'],
            common.md5_encode(self['url']),
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


class ZhihuQuestionItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class ZhihuQuestionItem(scrapy.Item):
    question_id = scrapy.Field(input_processor=MapCompose(int))
    topics = scrapy.Field(output_processor=Join(','))
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answers = scrapy.Field()
    comments = scrapy.Field(
        input_processor=MapCompose(
            lambda comments:
            common.word_eliminator(comments) if comments else 0
        )
    )
    follower_and_views = scrapy.Field(output_processor=MapCompose(int))
    created_time = scrapy.Field()
    updated_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def insert_sql_with_params(self):
        insert_sql = '''
            INSERT INTO zhihu_spider.question (
                question_id,
                topics,
                url,
                title,
                content,
                answers,
                comments,
                follower,
                views,
                created_time,
                updated_time,
                crawl_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (question_id) DO UPDATE
                SET content = excluded.content,
                    answers = excluded.answers,
                    comments = excluded.comments,
                    follower = excluded.follower,
                    views = excluded.views,
                    updated_time = excluded.updated_time,
                    crawl_updated_time = excluded.crawl_time
            '''
        params = (
            self['question_id'],
            self['topics'],
            self['url'],
            self['title'],
            self['content'],
            self['answers'],
            self['comments'],
            self['follower_and_views'][0],
            self['follower_and_views'][1],
            self['created_time'],
            self['updated_time'],
            self['crawl_time']
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

    def insert_sql_with_params(self):
        insert_sql = '''
            INSERT INTO zhihu_spider.answer (
                answer_id,
                url,
                question_id,
                author_id,
                content,
                votes,
                comments,
                created_time,
                updated_time,
                crawl_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (answer_id) DO UPDATE
                SET content = excluded.content,
                    votes = excluded.votes,
                    comments = excluded.comments,
                    updated_time = excluded.updated_time,
                    crawl_updated_time = excluded.crawl_time
            '''
        params = (
            self['answer_id'],
            self['url'],
            self['question_id'],
            self['author_id'],
            self['content'],
            self['votes'],
            self['comments'],
            common.format_timestamp(self['created_time']),
            common.format_timestamp(self['updated_time']),
            self['crawl_time']
        )

        return insert_sql, params
