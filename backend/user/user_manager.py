# coding=utf-8
# author: Lan_zhijiang
# desciption: The code manage users
# date: 2020/10/2

import json
from backend.database.memcached import GtdMemcachedManipulator


class GtdUserManager():

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting
        
        self.memcached_manipulator = GtdMemcachedManipulator(log, setting) 

    def add_user(self, account, password, email):

        """
        添加用户
        :param account: 账户名
        :param password: 密码(md5)
        :param email: 电子邮箱
        :return bool
        """
        user_info = json.load(open("./backend/data/json/user_info_template.json", "r", encoding="utf-8"))
        user_info["account"] = str(account)
        user_info["password"] = str(password)
        user_info["email"][0] = email
        if self.memcached_manipulator._add(account, user_info) == False:
            self.log.add_log("UserManager: Add user failed, this user had already exits. user: " + account, 3)
            return False
        else:
            self.log.add_log("UserManager: Add user successed!", 1)

    def update_user_info(self, account, info):

        """
        更新用户信息
        :param account: 账户名
        :param info: 要更新的信息
        :return bool
        """
        if type(info) != dict:
            self.log.add_log("UserManager: Failed to update user info: info must be a dict", 3)
            return False

        user_info = self.memcached_manipulator._get(account)
        
        for now_key in info.keys():
            try:
                self.log.add_log("UserManager: Updating " + str(now_key) + "'s info", 1)
                user_info[now_key] = info[now_key]
            except KeyError:
                self.log.add_log("User Manager: can't find " + str(now_key) + " in user_info, skip!", 3)
        
        self.memcached_manipulator._replace(account, user_info)
        return True

    def get_user_info(self, accounts):

        """
        获取用户信息（可多个）
        :param account: 账户名 list
        :return dict
        """
        if type(accounts) != list:
            self.log.add_log("UserManager: Param 'account' must be a list!", 3)
            return False
        
        user_info = self.memcached_manipulator._get_multi(accounts)

        for account in accounts:
            self.log.add_log("UserManager: Getting " + str(account) + "'s info", 1)
            if user_info[account] is None:
                self.log.add_log("UserManager: Can't find " + str(account), 3)
        
        return user_info

        # add_user_group  set_user_group  delete_user_group  update_user_group_info
