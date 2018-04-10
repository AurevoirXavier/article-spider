# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, MapCompose, TakeFirst, Join

from StupidSpider.util.common import *


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
    post_date = scrapy.Field(output_processor=Compose(
        lambda text: datetime.strptime(re.sub(r'[ \r\n·]', '', text[0]), '%Y/%m/%d')
    ))
    category = scrapy.Field()
    tag = scrapy.Field(
        input_processor=MapCompose(lambda text: None if '评论' in text else text),
        output_processor=Join(',')
    )
    content = scrapy.Field()
    votes = scrapy.Field(input_processor=MapCompose(int))
    bookmarks = scrapy.Field(input_processor=MapCompose(jobbole_dot_eliminator))
    comments = scrapy.Field(input_processor=MapCompose(jobbole_dot_eliminator))

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
            md5_encode(self['url']),
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
    comments = scrapy.Field(input_processor=MapCompose(digit_at_head))
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
            format_timestamp(self['created_time']),
            format_timestamp(self['updated_time']),
            self['crawl_time']
        )

        return insert_sql, params


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    url = scrapy.Field()
    position = scrapy.Field()
    salary = scrapy.Field(output_processor=MapCompose(lagou_format_salary))
    city = scrapy.Field(input_processor=MapCompose(slash_eliminator))
    experience = scrapy.Field(output_processor=MapCompose(lagou_format_experience))
    degree_require = scrapy.Field(input_processor=MapCompose(slash_eliminator))
    type = scrapy.Field()
    publish_time = scrapy.Field(input_processor=MapCompose(lagou_format_time))
    label = scrapy.Field(output_processor=Join(','))
    advantage = scrapy.Field()
    description = scrapy.Field()
    address = scrapy.Field()
    company_name = scrapy.Field()
    company_page = scrapy.Field()
    crawl_time = scrapy.Field()

    def insert_sql_with_params(self):
        insert_sql = '''
            INSERT INTO lagou_spider.job (
                url,
                url_id,
                position,
                salary_min,
                salary_max,
                city,
                experience_min,
                experience_max,
                degree_require,
                type,
                publish_time,
                label,
                advantage,
                description,
                address,
                company_name,
                company_page,
                crawl_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url_id) DO NOTHING
            '''
        params = (
            self['url'],
            md5_encode(self['url']),
            self['position'],
            self['salary'][0],
            self['salary'][1],
            self['city'],
            self['experience'][0],
            self['experience'][1],
            self['degree_require'],
            self['type'],
            self['publish_time'],
            self.get('label', default=''),
            self['advantage'],
            self['description'],
            self['address'],
            self['company_name'],
            self['company_page'],
            self['crawl_time']
        )

        return insert_sql, params
