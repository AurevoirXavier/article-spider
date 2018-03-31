# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonExporterPipeline:
    def __init__(self):
        self.file = open('article.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf8', ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)

        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


class ArticleImgPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, d in results:
            if ok:
                item['front_img_path'] = d['path']

        return item
