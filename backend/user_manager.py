# coding=utf-8
# author: Lan_zhijiang
# desciption: The code manage users
# date: 2020/10/2

from memcached import GtdMemcachedManipulator


class GtdUserManager():

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting
        
        self.gtd_memcached_manipulator = GtdMemcachedManipulator(log, setting) 

    def add_user(self, account, password, email, avatar):

        """
        添加用户
        :param account: 账户名
        :param password: 密码(md5)
        :param email: 电子邮箱
        :param avatar: 头像地址
        :return bool
        """
