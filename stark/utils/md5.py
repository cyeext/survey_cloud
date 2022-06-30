import hashlib


def gen_md5(original):
    """gen_md5.
    密码加密
    :param original: 原密码
    """
    ha = hashlib.md5(b'fnklklkjqefdas')
    ha.update(original.encode('utf-8'))
    return ha.hexdigest()
