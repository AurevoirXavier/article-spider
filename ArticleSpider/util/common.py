import hashlib
import hmac
import re
import datetime

from hashlib import sha1

SQL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
SQL_DATE_FORMAT = '%Y-%m-%d'


def md5_encode(url):
    if isinstance(url, str):
        url = url.encode('utf8')

    m = hashlib.md5()
    m.update(url)

    return m.hexdigest()


def get_first(l, default=None):
    for first in l:
        return first

    return default


def hmac_encode(grant_type, client_id, source, timestamp):
    signature = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=sha1)
    signature.update(
        bytes(
            grant_type + client_id + source + timestamp,
            'utf8'
        )
    )

    return signature.hexdigest()


def date_convert(text):
    date = re.sub(r'[ \r\n·]', '', text[0])
    if date:
        return datetime.datetime.strptime(date, '%Y/%m/%d')
    else:
        return datetime.datetime.now()


def jobbole_dot_eliminator(text):
    re_match = re.match(r'.*?(\d+).*', text)
    if re_match:
        return int(re_match.group(1))
    else:
        return 0


def symbol_eliminator(text):
    return re.sub(r',', '', text)


def word_eliminator(text):
    re_match = re.match(r'(\d+).*', text)
    if re_match:
        return int(re_match.group(1))
    else:
        return 0
