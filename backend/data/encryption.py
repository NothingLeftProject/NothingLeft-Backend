# coding=utf-8
# author: Lan_zhijiang
# description: 加密字符串（MD5 SHA256）
# date: 2022/5/1

import hashlib
import string
import random


class Encryption:

    def __init__(self):

        pass

    def md5(self, string_):

        """
        进行md5加密 32位！
        :param string_:
        :return:
        """
        return hashlib.md5(string_.encode('utf-8')).hexdigest()

    def sha1(self, string_):

        """
        进行sha1加密
        :param string_:
        :return:
        """
        return hashlib.sha1(string_.encode('utf-8')).hexdigest()

    def sha256(self, string_):

        """
        进行sha256加密
        :param string_:
        :return:
        """
        return hashlib.sha256(string_.encode('utf-8')).hexdigest()

    def generate_random_key(self):

        """
        生成随机钥匙
        :return:
        """
        maka = string.digits + string.ascii_letters
        maka_list = list(maka)
        x = [random.choice(maka_list) for i in range(6)]
        return ''.join(x)
