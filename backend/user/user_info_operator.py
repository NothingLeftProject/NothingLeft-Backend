# coding=utf-8
# author: Lan_zhijiang
# desciption: 用户信息管理器
# date: 2020/10/17

import json
from backend.user.user_manager import UserManager
from backend.database.mongodb import MongoDBManipulator


class UserInfoManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

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

    def get_users_all_info(self, accounts):

        """
        获取用户所有信息（可多个用户）
        :type accounts: list
        :param accounts: 账户名
        :return dict
        """
        if type(accounts) != list:
            self.log.add_log("UserInfoManager: Param 'account' must be a list!", 3)
            return False

        users_info = []

        for account in accounts:
            self.log.add_log("UserManager: Getting " + str(account).replace("user-", "") + "'s info", 1)
            user_info = self.mongodb_manipulator.get_document("user", account, {"_id": 0}, 2)

            for i in user_info:
                key = i.keys[0]
                user_info[key] = i[key]

            users_info.append(user_info)
            if users_info[account] is None:
                self.log.add_log("UserManager: Can't find " + str(account).replace("user-", ""), 3)

        return users_info

    def get_one_user_multi_info(self, account, keys):

        """
        获取单个用户的信息（支持多个信息，但只支持单个用户）
        :type keys: list
        :param keys: 要查询的keys
        :param account: 账户名
        :return:
        """
        result = {}

        for key in keys:
            self.log.add_log("UserInfoManager: try to get user- " + account + "'s " + key, 1)
            result[key] = self.mongodb_manipulator.get_document("user", account, {key: 1}, 2)[key]

        return result

    def get_multi_users_multi_info(self, accounts, keys):

        """
        获取多个用户多个信息
        :type keys: dict
        :type accounts: list
        :param accounts: 账户名列表 list
        :param keys: 要查询的keys，dict{account: [key, key, key]}
        :return:
        """
        result = {}
        for account in accounts:
            self.log.add_log("UserInfoManager: try to get " + account + "'s multi info", 1)
            result[account] = self.get_one_user_multi_info(account, keys[account])

        return result

    def set_avatar(self, account, avatar_data, img_type):

        """

        设置头像
        :param account: 账户名
        :param avatar_data: 头像二进制数据
        :param img_type: 头像图片文件类型
        :return:
        """

    def load_avatar(self, account):

        """
        加载头像——返回头像二进制数据和图片类型
        :param account: 账户名
        :return: img_data(bytes), img_type(str)
        """
