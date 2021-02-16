# coding=utf-8
# author: Lan_zhijiang
# description: 用户组管理器
# date: 2020/11/1

import json
from backend.database.mongodb import MongoDBManipulator


class UserGroupManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting
        self.user_group_info_template = json.load(open("./backend/data/json/user_group_info_template.json", "r", encoding="utf-8"))
        self.user_group_info_id_event_mapping = json.load(open("./backend/data/json/user_group_info_id_event_mapping.json", "r", encoding="utf-8"))

        self.mongodb_manipulator = MongoDBManipulator(log, setting)

    def add_users_into_group(self, accounts, target_group):

        """
        添加用户到用户组中
        :param accounts: 要被添加的用户
        :param target_group: 目标用户组名称
        :type accounts: list
        :return: bool
        """
        self.log.add_log("UserGroupManager: try to add users-%s" % accounts + " into user_group-%s" % target_group, 1)
        err_add_users = []

        if type(accounts) != list:
            self.log.add_log("UserGroupManager: wrong type of the param-accounts, it should be a list", 3)
            return False, "param-accounts wrong type"

        if self.mongodb_manipulator.is_collection_exist("user_group", target_group) is False:
            self.log.add_log("UserGroupManager: user_group: " + target_group + " is not exist", 3)
            return False, "user_group-%s" % target_group + " is not exist, add users into group fail"
        else:
            for account in accounts:
                if self.mongodb_manipulator.is_collection_exist("user", account) is False:
                    err_add_users.append(account)
                    self.log.add_log("UserGroupManager: user-%s" % account + " not exist, skip")
                    continue

                self.mongodb_manipulator.update_many_documents("user", account, {"_id": 4}, {"userGroup": target_group})

                user_list = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document("user_group", target_group, {"userList": 1}, 2),
                    ["userList"]
                )[0]["userList"]

                if account in user_list:
                    self.log.add_log("UserGroupManager: user-%s had already exists!" % account, 2)
                    err_add_users.append(account)

                user_list.append(account)
                if self.mongodb_manipulator.update_many_documents("user_group", target_group, {"_id": 1}, {"userList": user_list}) is False:
                    err_add_users.append(account)
                    self.log.add_log("UserGroupManager: add user-%s" % account + " into user_group-%s" % target_group + " fail, skip", 3)
                    continue
                else:
                    self.log.add_log("UserGroupManager: add user-%s" % account + " into user_group-%s" % target_group + " success", 1)

        if err_add_users is False:
            err = "users-%s" % err_add_users + " add fail"
        else:
            err = "success"

        return True, err

    def remove_users_from_group(self, accounts, target_group):

        """
        移除某个用户组的用户
        :param accounts: 用户名
        :param target_group: 用户组名
        :type accounts: list
        :return:
        """
        self.log.add_log("UserGroupManager: try to remove users-%s" % accounts + " from user-group-%s" % target_group, 1)
        err_remove_users = []

        if type(accounts) != list:
            self.log.add_log("UserGroupManager: wrong type of the param-accounts, it should be a list", 3)
            return False, "param-accounts wrong type"

        if self.mongodb_manipulator.is_collection_exist("user_group", target_group) is False:
            self.log.add_log("UserGroupManager: user_group-%s" % target_group + " is not exist", 3)
            return False, "user_group-%s" % target_group + " is not exist, remove users from group fail"
        else:
            for account in accounts:
                if self.mongodb_manipulator.is_collection_exist("user", account) is False:
                    err_remove_users.append(account)
                    self.log.add_log("UserGroupManager: user-%s" % account + " not exist, skip")
                    continue

                self.mongodb_manipulator.update_many_documents("user", account, {"_id": 4}, {"userGroup": None})

                try:
                    user_list = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("user_group", target_group, {"userList": 1}, 2),
                        ["userList"]
                    )[0]["userList"].remove(account)
                except ValueError:
                    err_remove_users.append(account)
                    self.log.add_log("UserGroupManager: fail to remove user-%s" % account + " from user_group-%s" % target_group
                                     + "because it's not exist", 1)
                    continue
                if self.mongodb_manipulator.update_many_documents("user_group", target_group, {"_id": 1}, {"userList": user_list}) is False:
                    err_remove_users.append(account)
                    self.log.add_log("UserGroupManager: database error, remove user-%s" % account + " from user-group-%s" % target_group + " fail", 3)
                else:
                    self.log.add_log("UserGroupManager: remove user-%s" % account + " from user_group-%s" % target_group + " success", 1)

        if err_remove_users is False:
            err = "users-%s" % err_remove_users + " remove fail"
        else:
            err = "success"

        return True, err

    def move_user_to_another_group(self, account, target_group):

        """
        将某用户从一用户组移到另一用户组
        :param account: 用户名
        :param target_group: 目标用户组
        :return: bool, str
        """
        self.log.add_log("UserGroupManager: move user-%s" % account + " to user_group-%s" % target_group, 1)

        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("UserGroupManager: move fail, user-%s" % account + " not exist", 3)
            return False, "user-%s" % account + " not exist"
        else:
            if self.mongodb_manipulator.is_collection_exist("user_group", target_group) is False:
                self.log.add_log("UserGroupManager: move fail! target_group-%s" % target_group + " not exist", 3)
                return False, "target_group-%s" % target_group + " not exist"
            else:
                from_group = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document("user", account, {"userGroup": 1}, 2),
                    ["userGroup"]
                )[0]["userGroup"]

                try:
                    from_group_user_list = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("user_group", from_group, {"userList": 1}, 2),
                        ["userList"]
                    )[0]["userList"].remove(account)
                except ValueError:
                    self.log.add_log("UserGroupManager: user-group-%s" % from_group + " does not exist, wrong record", 3)
                    return False, "wrong record of user's userGroup, cannot be found"

                target_group_user_list = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document("user_group", target_group, {"userList": 1}, 2),
                    ["userList"]
                )[0]["userList"].append(account)
                result_3 = self.mongodb_manipulator.update_many_documents("user_group", from_group, {"_id": 1}, {"userList": from_group_user_list})
                result_4 = self.mongodb_manipulator.update_many_documents("user_group", target_group, {"_id": 1}, {"userList": target_group_user_list})
                if result_3 is True and result_4 is True:
                    self.log.add_log("UserGroupManager: move user success", 1)
                    return True, "success"
                else:
                    self.log.add_log("UserGroupManager: move user fail", 3)
                    return False, "database error"

    def add_user_group(self, user_group, permissions_list=None):

        """
        创建用户组
        :param user_group: 用户组名
        :param permissions_list: 初始化的权限组
        :return: bool
        """
        if permissions_list is None:
            permissions_list = []
        self.log.add_log("UserGroupManager: add user group-%s" % user_group, 1)

        if self.mongodb_manipulator.is_collection_exist("user_group", user_group) is True:
            self.log.add_log("UserGroupManager: user_group-%s" % user_group + " had already exists", 3)
            return False, "user_group-%s" % user_group + " had already exists"
        else:

            user_group_info = self.user_group_info_template   # WARNING: must use like this to make sure it won't change raw data
            user_group_info[0]["user_group"] = user_group
            user_group_info[2]["permissionsList"] = permissions_list

            result_1 = self.mongodb_manipulator.add_collection("user_group", user_group)
            result_2 = self.mongodb_manipulator.add_many_documents("user_group", user_group, user_group_info)
            if result_1 and result_2:
                return True, "success"
            else:
                self.log.add_log("UserGroupManager: add user_group-%s fail because of database error" % user_group, 3)
                return False, "database error"

    def remove_user_group(self, user_group):

        """
        删除用户组
        :param user_group: 用户组名
        :return: bool
        """
        self.log.add_log("UserGroupManager: remove user_group-%s" % user_group, 1)

        if self.mongodb_manipulator.is_collection_exist("user_group", user_group) is False:
            self.log.add_log("UserGroupManager: user_group-%s" % user_group + " is not exists", 3)
            return False, "user_group-%s" % user_group + " is not exists"
        else:
            if self.mongodb_manipulator.delete_collection("user_group", user_group):
                return True, "success"
            else:
                self.log.add_log("UserGroupManager: remove user_group-%s fail because of database error" % user_group, 3)
                return False, "database error"

    def update_group_info(self, user_group, param):

        """
        更新用户组信息（全部）
        :param user_group: 用户组名
        :param param: 用户组信息
        :return:
        """
        self.log.add_log("UserGroupManager: update user-group-%s's info" % user_group, 1)
        if self.mongodb_manipulator.is_collection_exist("user_group", user_group) is False:
            self.log.add_log("UserGroupManager: user_group-%s does not exist" % user_group, 1)
            return False, "user_group-%s not exist" % user_group
        else:
            fail_update_keys = []
            need_updated_ids = []   # update's = updated + n.
            for key in param:
                try:
                    id = self.user_group_info_id_event_mapping[key]
                except KeyError:
                    self.log.add_log("UserGroupManager: Can't find key-%s in user_group_info_template, skip", 2)
                    fail_update_keys.append(key)
                    del param[key]
                    continue
                else:
                    need_updated_ids.append(id)

            result = self.mongodb_manipulator.update_many_documents("user_group", user_group, {"_id": need_updated_ids}, param)
            if result is False:
                self.log.add_log("UserGroupManager: update user_group-%s fail because of database error" % user_group, 3)
                return False, "database error"
            else:
                if fail_update_keys:
                    return True, "fail to update this key(s)-%s" % fail_update_keys
                else:
                    return True, "success"

    def add_group_info(self, user_group, param):

        """
        设置用户组信息（个别）
        :type param: dict
        :param user_group: 用户组名
        :param param: key->value的dict
        :return: bool
        """
