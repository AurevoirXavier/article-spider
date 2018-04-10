import re
import hmac
import hashlib

from hashlib import sha1
from datetime import datetime

SQL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
SQL_DATE_FORMAT = '%Y-%m-%d'


def md5_encode(text):
    if isinstance(text, str):
        text = text.encode('utf8')

    m = hashlib.md5()
    m.update(text)

    return m.hexdigest()


def take_first(iterable, default=None):
    for first in iterable:
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


def jobbole_dot_eliminator(text):
    re_match = re.match(r'.*?(\d+).*', text)
    if re_match:
        return int(re_match.group(1))
    else:
        return 0


def word_eliminator(text):
    re_match = re.match(r'(\d+).*', text)
    if re_match:
        return int(re_match.group(1))
    else:
        return 0


def format_timestamp(timestamp):
    return datetime \
        .fromtimestamp(timestamp) \
        .strftime(SQL_DATETIME_FORMAT)


def now():
    return datetime \
        .now() \
        .strftime(SQL_DATETIME_FORMAT)
