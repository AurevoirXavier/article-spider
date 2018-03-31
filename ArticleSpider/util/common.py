import hashlib


def md5_encode(url):
    if isinstance(url, str):
        url = url.encode('utf8')

    m = hashlib.md5()
    m.update(url)

    return m.hexdigest()
