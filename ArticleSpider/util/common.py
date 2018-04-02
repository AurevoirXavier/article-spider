import hashlib
import hmac

from hashlib import sha1


def md5_encode(url):
    if isinstance(url, str):
        url = url.encode('utf8')

    m = hashlib.md5()
    m.update(url)

    return m.hexdigest()


def hmac_encode(grant_type, client_id, source, timestamp):
    signature = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=sha1)
    signature.update(
        bytes(
            grant_type + client_id + source + timestamp,
            'utf8'
        )
    )

    return signature.hexdigest()
