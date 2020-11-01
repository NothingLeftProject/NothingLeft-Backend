# coding=utf-8
# author: Lan_zhijiang
# desciption: 用户管理器
# date: 2020/11/1

import hashlib
import hmac


class Encryption():

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

    def md5(self, string):

        """
        进行md5加密
        :param string:
        :return:
        """
        md5 = hashlib.md5()
        md5.update(string.encode("utf-8"))
        return md5.hexdigest()

    def sha1(self, string):

        """
        进行sha1加密
        :param string:
        :return:
        """
        sha1 = hashlib.sha1()
        sha1.update(string.encode("utf-8"))
        return sha1.hexdigest()

    def hmac(self, string):

        """
        进行hmac加密
        :param string:
        :return:
        """
        hmca = hmac.new(bytes(string))
        hmca.update("nothing left is wonderful")
        return hmca.hexdigest()
