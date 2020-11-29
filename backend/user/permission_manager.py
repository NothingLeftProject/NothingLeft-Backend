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
            self.log.add_log("UserPermissionManager: get permissions list from memcached success", 1)

        return permissions_list

    def write_user_permissions(self, account, permissions_list):

        """
        写入一个用户的权限
        :param account: 账户名
        :param permissions_list: 此用户被允许的权限
        :return: bool
        """
        self.log.add_log("UserPermissionManager: try to write " + account + "'s permissions in", 1)
        # write permissions into user
        # verify is the user_group this user belong to permissions are different from now
        # yes->add differences to permissionDifferences and add user to differentUsers
        # no->do nothing

    def edit_user_permissions(self, account, permissions_to_change):

        """
        编辑用户权限
        :param account: 账户名
        :param permissions_to_change: 要修改的权限 [{"permission_name": bool}]
        :type permissions_to_change: list[dict]
        :return: bool
        """
        self.log.add_log("UserPermissionManager: editing " + account + "'s permission", 1)

        # get now permissions list
        # change now_permissions_list as permissions_to_change (for permission in)
        # write_user_permissions
