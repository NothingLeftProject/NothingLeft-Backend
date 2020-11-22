# coding=utf-8
# author: Lan_zhijiang
# desciption: 用户信息管理器
# date: 2020/10/17

import json
from backend.user.user_manager import UserManager
from backend.database.mongodb import MongoDBManipulator


class UerInfoManager():

    def __init__(self, account, log, setting):

        self.log = log
        self.setting = setting

        self.account = account
        self.account_info = self.get_user_info([account])
        self.gtd_user_manager = UserManager(log, setting)
        self.mongodb_manipulator = MongoDBManipulator(log, setting)

        self.user_info_template = json.load(open("./data/json/user_info_template.json", "r", encoding="utf-8"))

    def update_user_info(self, account, info):

        """
        更新用户信息
        :param account: 账户名
        :param info: 要更新的信息
        :type info: dict
        :return bool
        """
        result = True
        if type(info) != dict:
            self.log.add_log("UserInfoManager: Failed to update user info: info must be a dict", 3)
            return False

        key_list = info.keys()
        for event in self.user_info_template:
            if event.keys[1] in key_list:  # needs to verify
                try:
                    if self.mongodb_manipulator.update_many_documents("user", account, {"_id": event["_id"]}, info[event.keys[1]]) is False:
                        self.log.add_log("UserInfoManager: meet database error while updating " + event.keys[1] + ", skip", 3)
                        result = False
                except KeyError:
                    self.log.add_log("UserInfoManager: can not find " + event.keys[1] + ", in your info list", 3)
                    result = False
        return result

    def get_user_info(self, accounts):

        """
        获取用户信息（可多个）
        :param accounts: 账户名 list
        :return dict
        """
        if type(accounts) != list:
            self.log.add_log("UserInfoManager: Param 'account' must be a list!", 3)
            return False

        for i in range(0, len(accounts)):
            accounts[i] = "user-" + accounts[i]

        user_info = self.mongodb_manipulator._get_multi(accounts)

        for account in accounts:
            self.log.add_log("UserManager: Getting " + str(account).replace("user-", "") + "'s info", 1)
            if user_info[account] is None:
                self.log.add_log("UserManager: Can't find " + str(account).replace("user-", ""), 3)

        return user_info

    def reset_param(self, account):

        """
        将给出的参数进行判断，然后重置「减少重复代码」
        :param account: 账户名
        :return:
        """
        if account is None:
            account = self.account
            account_info = self.account_info
        else:
            account_info = self.get_user_info([account])

        return account, account_info

    def set_info(self, key, value, account=None):

        """
        设置用户的指定信息
        :param key: 用户信息dict中要被设置的那个key
        :param value: 要设置为的value
        :param account: 账户名
        :return:
        """
        account, account_info = self.reset_param(account)

        self.log.add_log("UserInfoManager: Set " + account + " 's " + key + " to " + str(value), 1)
        account_info[key] = value
        self.account_info = account_info

        return self.update_user_info(account, account_info)

    def get_info(self, key, account=None):

        """
        获取用户的指定信息
        :param key: 用户信息dict中要被设置的那个key
        :param value: 要设置为的value
        :param account: 账户名
        :return:
        """
        account, account_info = self.reset_param(account)

        value = account_info[key]
        self.log.add_log("UserInfoManager: Get " + account + " 's " + key + " :" + value, 1)

        return value
