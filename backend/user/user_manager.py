# coding=utf-8
# author: Lan_zhijiang
# desciption: 用户管理器
# date: 2020/10/2

import json
from backend.data.encryption import Encryption
from backend.database.memcached import MemcachedManipulator


class UserManager():

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.encryption = Encryption(log, setting)
        self.memcached_manipulator = MemcachedManipulator(log, setting)

    def add_user(self, account, password, email, user_type="user"):

        """
        添加用户
        :param account: 账户名
        :param password: 密码(md5)
        :param email: 电子邮箱
        :param user_type: 用户类型
        :return bool
        """
        if "/" in account or "." in account:
            self.log.add_log("UserManager: '/' or '.' is banned in account name", 3)
            return False

        user_info = json.load(open("./backend/data/json/user_info_template.json", "r", encoding="utf-8"))
        user_info["account"] = str(account)
        user_info["password"] = str(password)
        user_info["email"][0] = email
        user_info["type"] = user_type
        if self.memcached_manipulator._add(account, user_info) is False:
            self.log.add_log("UserManager: Add user failed, this user had already exits. user: " + account, 3)
            return False
        else:
            self.log.add_log("UserManager: Add user successed!", 1)
            return True

    def delete_user(self, account):

        """
        删除某个用户
        :param account: 账户名
        :return:
        """
        self.log.add_log("UserManager: Delete user: " + account, 1)
        return self.memcached_manipulator._delete(account)

    def sign_up(self, param):

        """
        注册
        :param param: 注册数据
        :return: bool
        """
        self.log.add_log("UserManager: Start sign_up", 1)
        try:
            account = param["account"]
            password = param["password"]
            email = param["email"]
            user_type = param["user_type"]
        except KeyError:
            self.log.add_log("UserManager: sign_up: Your param is incomplete!", 3)
            return False
        else:
            password = self.encryption.md5(password)
            return self.add_user(account, password, email, user_type)

    def login(self, param):

        """
        登录
        :param param:
        :return: bool(fail) str(success)
        """
        try:
            account = param["account"]
            password = param["password"]
        except KeyError:
            self.log.add_log("UserManager: login: Your param is incomplete!", 3)
            return False
        else:
            self.log.add_log("UserManager: Try login " + account)
            password = self.encryption.md5(password)

            user_info = self.memcached_manipulator._get(account)
            if user_info is False:
                if password == user_info["password"]:
                    token = self.log.get_time_stamp() + account
                    self.setting["user"]["token"] = token
                    self.setting["user"]["account"] = account
                    self.setting["user"]["avatar"] = user_info["avatar"]

                    return token
                else:
                    self.log.add_log("UserManager: Your password is wrong!", 3)
                    return False
            else:
                self.log.add_log("UserManager: login: Can't find your account or something wrong with the memcached.", 3)
                return False
