# coding=utf-8
# author: Lan_zhijiang
# desciption: 用户管理器
# date: 2020/11/1

import hashlib
import hmac
import string
import random


class Encryption():

    def __init__(self):

        # self.log = log
        # self.setting = setting

        self.md5_ = hashlib.md5()
        self.sha1_ = hashlib.sha1()
        self.hmca_ = hmac.new(bytes(string))

    def md5(self, string):

        """
        进行md5加密 32位！
        :param string:
        :return:
        """
        self.md5_.update(string.encode("utf-8"))
        return self.md5_.hexdigest()

    def sha1(self, string):

        """
        进行sha1加密
        :param string:
        :return:
        """
        self.sha1_.update(string.encode("utf-8"))
        return self.sha1_.hexdigest()

    def hmac(self, string):

        """
        进行hmac加密
        :param string:
        :return:
        """
        self.hmca_.update(string)
        return self.hmca_.hexdigest()

    def generate_random_key(self):

        """
        生成随机钥匙
        :return:
        """
        maka = string.digits + string.ascii_letters
        maka_list = list(maka)
        x = [random.choice(maka_list) for i in range(6)]
        return ''.join(x)
