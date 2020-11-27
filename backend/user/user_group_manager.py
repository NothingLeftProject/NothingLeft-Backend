# coding=utf-8
# author: Lan_zhijiang
# description: 用户组管理器
# date: 2020/11/1

from backend.database.mongodb import MongoDBManipulator
from backend.user.permission_manager import PermissionManager


class UserGroupManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.mongodb_manipulator = MongoDBManipulator(log, setting)
        self.permission_manager = PermissionManager(log, setting)

    def add_user_into_group(self, account, group_name):

        """
        添加用户到用户组中
        :param account: 要被添加的用户
        :param group_name: 目标用户组名称
        :return: bool
        """
        self.log.add_log("UserGroupManager: try to add " + account + " into " + group_name)

        if self.mongodb_manipulator.is_collection_exist("user_group", group_name) is False:
            self.log.add_log("UserGroupManager: user_group: " + group_name + " is not exists", 3)
            return False
        else:
            self.mongodb_manipulator.update_many_documents("user", account, {"_id": 4}, {"userGroup": group_name})

            user_list = self.mongodb_manipulator.get_document("user_group", group_name, {"userList": 1}, 1)["userList"].append(account)
            if self.mongodb_manipulator.update_many_documents("user_group", group_name, {"_id": 1}, {"userList": user_list}) is False:
                self.log.add_log("UserGroupManager: add " + account + " into " + group_name + " fail", 3)
            else:
                self.log.add_log("UserGroupManager: add " + account + " into " + group_name + " success", 3)

    def remove_user_from_group(self, account, group_name):

        """
        移除某个用户组的用户
        :param account: 用户名
        :param group_name: 用户组名
        :return:
        """
        self.log.add_log("UserGroupManager: try to remove " + account + " from " + group_name)

        if self.mongodb_manipulator.is_collection_exist("user_group", group_name) is False:
            self.log.add_log("UserGroupManager: user_group: " + group_name + " is not exists", 3)
            return False
        else:
            self.mongodb_manipulator.update_many_documents("user", account, {"_id": 4}, {"userGroup": None})

            user_list = self.mongodb_manipulator.get_document("user_group", group_name, {"userList": 1}, 1)["userList"].remove(account)
            if self.mongodb_manipulator.update_many_documents("user_group", group_name, {"_id": 1}, {"userList": user_list}) is False:
                self.log.add_log("UserGroupManager: remove " + account + " from " + group_name + " fail", 3)
            else:
                self.log.add_log("UserGroupManager: remove " + account + " from " + group_name + " success", 3)

    def move_user_to_another_group(self, account, from_group, to_group):

        """
        将某用户从一用户组移到另一用户组
        :param account: 用户名
        :param from_group: 原用户组
        :param to_group: 目标用户组
        :return: bool
        """

    def add_user_group(self, name):

        """
        创建用户组
        :param name: 用户组名
        :return:
        """
        self.log.add_log("UserGroupManager: add user group: " + name, 1)

        if self.mongodb_manipulator.is_collection_exist("user_group", name) is True:
            self.log.add_log("UserGroupManager: user_group: " + name + " had already exists", 3)
            return False
        else:
            return self.mongodb_manipulator.add_collection("user_group", name)

    def delete_user_group(self, name):

        """
        删除用户组
        :param name: 用户组名
        :return:
        """

    def update_group_info(self, name, param):

        """
        更新用户组信息（全部）
        :param name: 用户组名
        :param param: 用户组信息
        :return:
        """

    def add_group_info(self, name, key, value=None):

        """
        设置用户组信息（个别）
        :param name: 用户组名
        :param key: 键
        :param value: 值
        :return:
        """
