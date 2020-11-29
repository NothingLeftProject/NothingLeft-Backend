# coding=utf-8
# author: Lan_zhijiang
# description: 用户权限管理器
# date: 2020/11/23

from backend.database.mongodb import MongoDBManipulator
from backend.database.memcached import MemcachedManipulator
from backend.user.user_group_manager import UserGroupManager
from backend.user.user_info_operator import UserInfoManager


class UserPermissionManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.user_info_manager = UserInfoManager(log, setting)
        self.user_group_manager = UserGroupManager(log, setting)
        self.mongodb_manipulator = MongoDBManipulator(log, setting)
        self.memcached_manipulator = MemcachedManipulator(log, setting)

    def get_user_permissions(self, account, cache_to_memcached=True):

        """
        获取一个用户的权限组
        :param account: 账户名
        :param cache_to_memcached: 是否缓存到memcached
        :return: list/False
        """
        self.log.add_log("UserPermissionManager: getting the permissions list of " + account, 1)

        permissions_list = self.memcached_manipulator._get("permissions-" + account)
        if permissions_list is None or cache_to_memcached is False:
            group_name = self.mongodb_manipulator.get_document("user", account, {"userGroup": 1}, 2)["userGroup"]
            if group_name is False:
                self.log.add_log("UserPermissionManager: can't find the account-" + account + " or something wrong", 3)
                return False

            permissions_list = self.mongodb_manipulator.get_document("user_group", group_name, {"permissionsList": 1}, 2)["PermissionsList"]
            different_user_list = self.mongodb_manipulator.get_document("user_group", group_name, {"differentUsers": 1}, 2)["differentUsers"]

            if account in different_user_list:
                permission_difference = self.mongodb_manipulator.get_document("user_group", group_name, {"permissionDifferences": 1}, 2)["permissionDifferences"][account]
                try:
                    for permission in permission_difference:
                        permission_name = permission.keys[0]
                        if permission[permission_name] is True:
                            permissions_list.append(permission_name)
                        else:
                            permissions_list.remove(permission_name)
                except TypeError:
                    self.log.add_log("UserPermissionManager: get_user_permission: something went wrong with database",
                                     3)
                    return False
        else:
            self.log.add_log("UserPermissionManager: get permissions list from memcached success")

        return permissions_list
