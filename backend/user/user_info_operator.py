# coding=utf-8
# author: Lan_zhijiang
# desciption: 用户信息管理器
# date: 2020/10/17

import json
import time

from backend.database.mongodb import MongoDBManipulator


class UserInfoManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.mongodb_manipulator = MongoDBManipulator(log, setting)

        self.user_info_id_event_mapping = json.load(open("./backend/data/json/user_info_id_event_mapping.json", "r", encoding="utf-8"))
        self.all_user_info_keys = list(self.user_info_id_event_mapping.keys())

    def update_user_info(self, account, info):

        """
        更新用户信息
        :param account: 账户名
        :param info: 要更新的信息
        :type info: dict
        :return bool
        """
        not_found_keys = []
        res, err = True, ""
        if type(info) != dict:
            self.log.add_log("UserInfoManager: Failed to update user info: info must be a dict", 3)
            return False, "the type of info is wrong"

        key_list = info.keys()
        for key in key_list:
            try:
                if key == "permissionsList" and account != "root":
                    self.log.add_log("UserInfoManager: It's not allow normal user to change permissionsList", 1)
                    raise KeyError

                if self.mongodb_manipulator.update_many_documents("user", account, {"_id": self.user_info_id_event_mapping[key]}, {key: info[key]}) is False:
                    self.log.add_log("UserInfoManager: meet database error while updating " + key + ", skip and wait", 3)
                    res, err = False, "database error"
                    time.sleep(0.1)
                    continue
            except KeyError:
                self.log.add_log("UserInfoManager: can not find " + key + ", in your info list", 3)
                not_found_keys.append(key)
                res, err = False, "key-" + str(not_found_keys) + " does not exists or '_id' is not exists"
                continue
        
        return res, err

    def get_users_all_info(self, accounts):

        """
        获取用户所有信息（可多个用户）
        :type accounts: list
        :param accounts: 账户名
        :return dict
        """
        if type(accounts) != list:
            self.log.add_log("UserInfoManager: Param 'account' must be a list!", 3)
            return False, "the type of param is wrong"

        users_info = {}
        not_found_users = []
        res = "success"

        for account in accounts:
            self.log.add_log("UserInfoManager: Getting user-" + str(account) + "'s info", 1)
            raw_user_info = self.mongodb_manipulator.get_document("user", account, mode=0)
            if raw_user_info is False:
                not_found_users.append(account)
                self.log.add_log("UserInfoManager: Can't find user-%s" % account, 1)

            user_info = {}
            for info in raw_user_info:
                key = list(info.keys())[-1]
                user_info[key] = info[key]

            users_info[account] = user_info

        if not_found_users:
            res = "user-" + str(not_found_users) + " is not exist"
        return users_info, res

    def get_one_user_multi_info(self, account, keys):

        """
        获取单个用户的信息（支持多个信息，但只支持单个用户）
        :type keys: list
        :param keys: 要查询的keys
        :param account: 账户名
        :return:
        """
        result = {}
        not_found_keys = []
        res = "success"

        for key in keys:
            self.log.add_log("UserInfoManager: try to get user- " + account + "'s " + key, 1)

            if key in self.all_user_info_keys:
                result_ = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document("user", account, {key: 1}, 2),
                    [key]
                )
                result[key] = result_[0][key]
            else:
                not_found_keys.append(key)
                continue

        if not_found_keys:
            res = "key-" + str(not_found_keys) + " is not exist"
        return result, res

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
        info_not_found_users = []
        err = "success"

        if type(keys) != dict:
            self.log.add_log("UserInfoManager: In get_multi_multi_info, param-keys must be a dict", 3)
            return False, "param-keys type error"

        for account in accounts:
            self.log.add_log("UserInfoManager: try to get user-%s's multi info" % account, 1)

            if self.mongodb_manipulator.is_collection_exist("user", account) is False:
                self.log.add_log("UserInfoManager: user-%s is not exist" % account, 1)
                info_not_found_users.append(account)
                continue

            result_, err_ = self.get_one_user_multi_info(account, keys[account])

            if err_ != "success":
                self.log.add_log("UserInfoManager: " + err_, 1)
                info_not_found_users.append(account)
                continue
            else:
                result[account] = result_

        if info_not_found_users:
            err = "user-" + str(info_not_found_users) + "'s info can't be found or user not exist"
        return result, err

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
