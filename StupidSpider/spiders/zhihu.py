# -*- coding: utf-8 -*-
import scrapy
import re
import base64
import json

from scrapy import Request, FormRequest
from time import time
from StupidSpider.util.common import hmac_encode, now, format_timestamp, take_first, symbol_eliminator
from PIL import Image
from StupidSpider.util.secret.secret import ZHIHU_USERNAME, ZHIHU_PASSWORD
from urllib.parse import urljoin
from StupidSpider.items import ZhihuAnswerItem, ZhihuQuestionItem, ZhihuQuestionItemLoader

SIGN_UP_ADDRESS = 'https://www.zhihu.com/signup'
SIGN_IN_ADDRESS = 'https://www.zhihu.com/api/v3/oauth/sign_in'
AUTH_ADDRESS = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
HEADERS = {
    'Host': 'www.zhihu.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
    'Referer': 'https://www.zhihu.com/'
}
FORM_DATA = {
    'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
    'grant_type': 'password',
    'source': 'com.zhihu.web',
    'username': '',
    'password': '',
    'lang': 'en',
    'ref_source': 'homepage'
}


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    sign_up_address = SIGN_UP_ADDRESS
    sign_in_address = SIGN_IN_ADDRESS
    auth_address = AUTH_ADDRESS
    headers = HEADERS.copy()
    form_data = FORM_DATA.copy()

    answer_api = 'https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D' \
                 '.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action' \
                 '%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count' \
                 '%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings' \
                 '%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion' \
                 '%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp' \
                 '%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count' \
                 '%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}'

    def start_requests(self):
        return [Request(self.sign_up_address, headers=self.headers, callback=self._sign_in)]

    def _sign_in(self, response):
        headers = self.headers.copy()
        headers.update({
            'Origin': 'https://www.zhihu.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'br, gzip, deflate',
            'Accept-Language': 'en-us',
            'DNT': '1',
            'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
            'X-Xsrftoken': re.match(
                r'_xsrf=([\w|-]+)',
                response.headers.getlist(b'Set-Cookie')[1].decode('utf8')
            ).group(1)
        })

        timestamp = str(int(time() * 1000))
        self.form_data.update({
            'username': ZHIHU_USERNAME,
            'password': ZHIHU_PASSWORD,
            'timestamp': timestamp,
            'signature': hmac_encode(
                self.form_data['grant_type'],
                self.form_data['client_id'],
                self.form_data['source'],
                timestamp
            ),
            'captcha': ''
        })

        yield Request(
            self.auth_address,
            headers=headers,
            meta={
                'headers': headers,
                'form_data': self.form_data
            },
            callback=self._auth
        )

    def _auth(self, response):
        headers = response.meta.get('headers')

        if re.search(r'true', response.text):
            yield Request(
                self.auth_address,
                method='PUT',
                headers=headers,
                meta={
                    'headers': headers,
                    'form_data': response.meta.get('form_data')
                },
                callback=self._post_captcha
            )
        else:
            yield FormRequest(
                url=self.sign_in_address,
                headers=headers,
                formdata=response.meta.get('form_data'),
                callback=self._online_status
            )

    def _post_captcha(self, response):
        headers = response.meta.get('headers')
        form_data = response.meta.get('form_data')
        base64_img = re.findall(
            r'"img_base64":"(.+)"',
            response.text,
            re.S
        )[0].replace(r'\n', '')

        with open('./util/captcha', 'wb') as f:
            f.write(base64.b64decode(base64_img))

        Image.open('./util/captcha').show()

        input_text = input('Captcha: ')

        form_data.update({
            'captcha': input_text
        })

        yield FormRequest(
            url=self.auth_address,
            headers=headers,
            formdata={
                'input_text': input_text
            },
            meta={
                'headers': headers,
                'form_data': form_data
            },
            callback=self._auth_with_captcha
        )

    def _auth_with_captcha(self, response):
        yield FormRequest(
            url=self.sign_in_address,
            headers=response.meta.get('headers'),
            formdata=response.meta.get('form_data'),
            callback=self._online_status
        )

    def _online_status(self, response):
        if response.status == 201:
            for url in self.start_urls:
                yield Request(url, dont_filter=True, headers=self.headers)

    def parse(self, response):
        all_urls = [
            urljoin(response.url, url)
            for url in response.css('a::attr(href)').extract()
        ]

        for url in all_urls:
            re_match = re.match(r'(.*zhihu.com/question/(\d+))(/|$).*', url)
            if re_match:
                yield Request(
                    re_match.group(1),
                    headers=self.headers,
                    callback=self.parse_question
                )
                break
            else:
                yield Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        question_id = re.match(
            r'(.*zhihu.com/question/(\d+))(/|$).*',
            response.url
        ).group(2)

        zhihu_question_item_loader = ZhihuQuestionItemLoader(item=ZhihuQuestionItem(), response=response)
        zhihu_question_item_loader.add_value('question_id', question_id)
        zhihu_question_item_loader.add_css('topics', '.TopicLink .Popover div::text')
        zhihu_question_item_loader.add_value('url', response.url)
        zhihu_question_item_loader.add_css('title', 'h1.QuestionHeader-title::text')
        zhihu_question_item_loader.add_css('content', '.QuestionHeader-detail')
        zhihu_question_item_loader.add_value(
            'answers',
            int(
                symbol_eliminator(
                    response.css(
                        '.List-headerText span::text'
                    ).extract_first('0')
                )
            )
        )
        zhihu_question_item_loader.add_css('comments', '.QuestionHeader-Comment button::text')
        zhihu_question_item_loader.add_css('follower_and_views', '.NumberBoard-itemValue::attr(title)')
        zhihu_question_item_loader.add_value('crawl_time', now())

        yield Request(
            self.answer_api.format(question_id, 20, 0),
            headers=self.headers,
            meta={
                'loader': zhihu_question_item_loader
            },
            callback=self.parse_answer
        )

        self.parse(response)

    def parse_answer(self, response):
        answer_json = json.loads(response.text)

        if response.meta.get('loader'):
            loader = response.meta.get('loader')

            if answer_json['data']:
                answer = take_first(answer_json['data'])

                loader.add_value(
                    'created_time',
                    format_timestamp(
                        answer['question']['created']
                    )
                )
                loader.add_value(
                    'updated_time',
                    format_timestamp(
                        answer['question']['updated_time']
                    )
                )

                yield loader.load_item()
            else:
                yield Request(
                    loader._values['url'][0] + '/log',
                    headers=self.headers,
                    meta={
                        'loader': loader.load_item()
                    },
                    callback=self.parse_log
                )

        for answer in answer_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['answer_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id']
            answer_item['content'] = answer['content'] if 'content' in answer else answer['excerpt']
            answer_item['votes'] = answer['voteup_count']
            answer_item['comments'] = answer['comment_count']
            answer_item['created_time'] = answer['created_time']
            answer_item['updated_time'] = answer['updated_time']
            answer_item['crawl_time'] = now()

            yield answer_item

        if not answer_json['paging']['is_end']:
            yield Request(
                answer_json['paging']['next'],
                headers=self.headers,
                callback=self.parse_answer
            )

    def parse_log(self, response):
        item = response.meta.get('loader')

        item._values['created_time'] = response.css(
            '#zh-question-log-list-wrap>:last-child time::text'
        ).extract_first()
        item._values['updated_time'] = response.css(
            '#zh-question-log-list-wrap>:first-child time::text'
        ).extract_first()

        yield item
