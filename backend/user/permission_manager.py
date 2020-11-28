# coding=utf-8
# author: Lan_zhijiang
# description: 用户权限管理器
# date: 2020/11/23

from backend.database.mongodb import MongoDBManipulator
from backend.user.user_group_manager import UserGroupManager
from backend.user.user_info_operator import UserInfoManager


class UserPermissionManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.user_info_manager = UserInfoManager(log, setting)
        self.user_group_manager = UserGroupManager(log, setting)
        self.mongodb_manipulator = MongoDBManipulator(log, setting)

    def get_user_permissions(self, account):

        """
        获取一个用户的权限组
        :param account: 账户名
        :return: list/False
        """
        self.log.add_log("UserPermissionManager: getting the permissions list of " + account, 1)

        user_group = self.mongodb_manipulator.get_document("user", account, {"userGroup": 1}, 2)["userGroup"]



