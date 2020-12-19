# coding=utf-8
# author: Lan_zhijiang
# description: 用户权限管理器
# date: 2020/11/1

from backend.database.mongodb import MongoDBManipulator
from backend.database.memcached import MemcachedManipulator
from .user_group_manager import UserGroupManager


class UserPermissionManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.user_group_manager = UserGroupManager(log, setting)
        self.mongodb_manipulator = MongoDBManipulator(log, setting)
        self.memcached_manipulator = MemcachedManipulator(log, setting)

    def get_user_permissions(self, account, cache_to_memcached=True, ask_update=False):

        """
        获取一个用户的权限组
        :param account: 账户名
        :param cache_to_memcached: 是否缓存到memcached
        :param ask_update: 是否从缓存中获取
        :return: list/False
        """
        self.log.add_log("UserPermissionManager: getting the permissions list of " + account, 1)

        permissions_list = None
        if ask_update is False:
            permissions_list = self.memcached_manipulator._get("permissions-" + account)
        if permissions_list is None or cache_to_memcached is False:
            group_name = self.mongodb_manipulator.get_document("user", account, {"userGroup": 1}, 2)[0][
                "userGroup"]  # ATTENTION: error might be here
            if group_name is False:
                self.log.add_log("UserPermissionManager: can't find the account-" + account + " or something wrong", 3)
                return False, "user does not exists"

            permissions_list = self.mongodb_manipulator.get_document("user_group", group_name, {"_id": 2}, 2)[0][
                "PermissionList"]
            different_user_list = self.mongodb_manipulator.get_document("user_group", group_name, {"_id": 3}, 2)[0][
                "differentUsers"]

            if account in different_user_list:
                permission_difference = \
                self.mongodb_manipulator.get_document("user_group", group_name, {"permissionDifferences": 1}, 2)[0][
                    "permissionDifferences"][account]
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
                    return False, "database error"
        else:
            self.log.add_log("UserPermissionManager: get permissions list from memcached success", 1)

        self.log.add_log("UserPermissionManager: " + account + "'s perms: " + str(list(permissions_list)), 0,
                         is_print=False)
        return list(permissions_list)

    def write_user_permissions(self, account, new_permissions_list):

        """
        写入一个用户的权限(覆盖用户，比较用户组)
        :type new_permissions_list: list
        :param account: 账户名
        :param new_permissions_list: 此用户被允许的权限
        :return: bool
        """
        self.log.add_log("UserPermissionManager: try to write " + account + "'s permissions in", 1)

        # write permissions into user_document
        self.mongodb_manipulator.update_many_documents("user", account, query={"_id": 12}, values=new_permissions_list)

        group_name = self.mongodb_manipulator.get_document("user", account, query={"userGroup": 1}, mode=2)[0][
            "userGroup"]
        group_permissions_list = \
        self.mongodb_manipulator.get_document("user_group", group_name, query={"permissionList": 1}, mode=2)[0][
            "permissionList"]
        different_list = []

        # verify is the user_group this user belong to permissions are different from now
        is_different = False
        for pmis in new_permissions_list:
            if pmis not in group_permissions_list:
                is_different = True
                different_list.append(pmis)

        # yes->add differences to permissionDifferences and add user to differentUsers
        if is_different:
            different_users = \
            self.mongodb_manipulator.get_document("user_group", group_name, query={"_id": 3}, mode=2)[0][
                "differentUsers"]
            different_users.append(account)
            self.mongodb_manipulator.update_many_documents("user_group", group_name, query={"_id": 3},
                                                           values=different_users)

            different_permissions_list = \
            self.mongodb_manipulator.get_document("user_group", group_name, query={"_id": 4}, mode=2)[0][
                "permissionDifferences"]
            different_permissions_list[account] = different_list
            self.mongodb_manipulator.update_many_documents("user_group", group_name, query={"_id": 4},
                                                           values=different_permissions_list)

        return True
        # no->do nothing

    def edit_user_permissions(self, account, permissions_to_change):

        """
        编辑用户权限
        :param account: 账户名
        :param permissions_to_change: 要修改的权限 [["permission_name", bool]]
        :type permissions_to_change: list[list]
        :return: bool
        """
        self.log.add_log("UserPermissionManager: editing " + account + "'s permission", 1)

        # get now permissions list
        raw_permissions_list = self.mongodb_manipulator.get_document("user", account, query={"_id": 12}, mode=2)[0][
            "permissionList"]

        # change now_permissions_list as permissions_to_change (for permission in)
        for permission in permissions_to_change:
            try:
                if permission[1]:
                    raw_permissions_list.append(permission[0])
                else:
                    raw_permissions_list.remove(permission[0])
            except IndexError:
                self.log.add_log("UserPermissionManager: wrong param for permission_to_change", 3)
                return False, "error format of permission_to_change"
            except KeyError:
                self.log.add_log("UserPermissionManager: permission: " + permission[0] + " is not exists", 3)
                return False, "permission " + permission[0] + " is not exists"

        # write_user_permissions
        self.mongodb_manipulator.update_many_documents("user", account, query={"_id": 12}, values=raw_permissions_list)
        return True, "success"