# coding=utf-8
# author: Lan_zhijiang
# description: 用户组管理器
# date: 2020/11/1

from backend.database.mongodb import MongoDBManipulator
from backend.database.memcached import MemcachedManipulator
from backend.user.user_info_operator import UserInfoManager


class UserGroupManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.mongodb_manipulator = MongoDBManipulator(log, setting)
        self.permission_manager = UserPermissionManager(log, setting)

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

            user_list = self.mongodb_manipulator.get_document("user_group", group_name, {"userList": 1}, 2)["userList"]
            if account in user_list:
                self.log.add_log("UserGroupManager: the account you want to add in had already exists!", 2)
                return False
            user_list.append(account)
            if self.mongodb_manipulator.update_many_documents("user_group", group_name, {"_id": 1}, {"userList": user_list}) is False:
                self.log.add_log("UserGroupManager: add " + account + " into " + group_name + " fail", 3)
                return False
            else:
                self.log.add_log("UserGroupManager: add " + account + " into " + group_name + " success", 1)
                return True

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

            user_list = self.mongodb_manipulator.get_document("user_group", group_name, {"userList": 1}, 2)["userList"].remove(account)
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
        self.log.add_log("UserGroupManager: try to move " + account + " from " + from_group + " to " + to_group, 1)

        if self.mongodb_manipulator.is_collection_exist("user_group", from_group) is False:
            self.log.add_log("UserGroupManager: move fail! from_group: " + from_group + " is not exists", 3)
            return False
        else:
            if self.mongodb_manipulator.is_collection_exist("user_group", to_group) is False:
                self.log.add_log("UserGroupManager: move fail! to_group: " + to_group + " is not exists", 3)
                return False
            else:
                result_1 = from_group_user_list = self.mongodb_manipulator.get_document("user_group", from_group, {"userList": 1}, 2)["userList"].remove(account)
                result_2 = to_group_user_list = self.mongodb_manipulator.get_document("user_group", to_group, {"userList": 1}, 2)["userList"].append(account)
                result_3 = self.mongodb_manipulator.update_many_documents("user_group", from_group, {"_id": 1}, {"userList": from_group_user_list})
                result_4 = self.mongodb_manipulator.update_many_documents("user_group", to_group, {"_id": 1}, {"userList": to_group_user_list})

        if result_1 is False or result_2 is False:
            self.log.add_log("UserGroupManager: move account fail because of the problem from the reading of database", 3)
            return False
        elif result_3 is False or result_4 is False:
            self.log.add_log("UserGroupManager: move account fail because of the problem from the writing of database", 3)
            return False
        else:
            return True

    def add_user_group(self, name):

        """
        创建用户组
        :param name: 用户组名
        :return: bool
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
        :return: bool
        """
        self.log.add_log("UserGroupManager: add user group: " + name, 1)

        if self.mongodb_manipulator.is_collection_exist("user_group", name) is False:
            self.log.add_log("UserGroupManager: user_group: " + name + " is not exists", 3)
            return False
        else:
            return self.mongodb_manipulator.delete_collection("user_group", name)

    def update_group_info(self, name, param):

        """
        更新用户组信息（全部）
        :param name: 用户组名
        :param param: 用户组信息
        :return:
        """

    def add_group_info(self, name, param):

        """
        设置用户组信息（个别）
        :type param: dict
        :param name: 用户组名
        :param param: key->value的dict
        :return: bool
        """


class UserPermissionManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.user_info_manager = UserInfoManager(log, setting)
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

