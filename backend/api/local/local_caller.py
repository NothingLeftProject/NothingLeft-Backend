# coding=utf-8
# author: Lan_zhijiang
# desciption 本地api
# date: 2020/11/15

from backend.user.user_manager import UserManager
from backend.user.user_info_operator import UserInfoManager
from backend.user.user_permission_mamanger import UserPermissionManager
from backend.user.user_group_manager import UserGroupManager


class LocalCaller:

    def __init__(self, log, setting, caller):

        self.log = log
        self.setting = setting
        self.caller = caller

        if self.caller == "root":
            self.not_root = False
        else:
            self.not_root = True

        self.user_manager = UserManager(log, setting)
        self.user_permission_manager = UserPermissionManager(log, setting)
        self.user_info_manager = UserInfoManager(log, setting)
        self.user_group_manager = UserGroupManager(log, setting)

    def user_login(self, param):

        """
        用户登录
        :return:
        """
        self.log.add_log("LocalCaller: start user_login", 1)

        result = {}

        try:
            account = param["account"]
            password = param["password"]
        except KeyError:
            self.log.add_log("LocalCaller: user_login: Your param is incomplete!", 3)
            return False, "param incomplete"
        else:
            password = self.user_manager.encryption.md5(password)
            res, err = self.user_manager.login(account, password)
            if res is False:
                return False, err
            else:
                result["token"] = res
                return result, err

    def user_logout(self, param):

        """
        用户登出
        :return:
        """
        self.log.add_log("LocalCaller: start user_logout", 1)

        try:
            account = param["account"]
        except KeyError:
            self.log.add_log("LocalCaller: user_sign_up: Your param is incomplete!", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_manager.logout(account)
            return res, err

    def user_sign_up(self, param):

        """
        用户注册
        :return: 
        """
        self.log.add_log("LocalCaller: start user_sign_up", 1)

        result = {}
        try:
            account = param["account"]
            password = param["password"]
            email = param["email"]
            user_group = param["userGroup"]
        except KeyError:
            self.log.add_log("LocalCaller: user_sign_up: Your param is incomplete!", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_manager.sign_up(account, password, email, user_group)
            if res is False:
                return False, err
            else:
                return result, err
    
    def user_delete(self, param):

        """
        删除用户
        :return:
        """
        self.log.add_log("LocalCaller: start user_delete", 1)
        
        result = {}
        try:
            account = param["account"]
        except KeyError:
            self.log.add_log("LocalCaller: user_delete: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_manager.delete_user(account)
            if res is False:
                return False, err
            else:
                return result, err

    def user_info_update(self, param):

        """
        更新用户信息
        :return:
        """
        self.log.add_log("LocalCaller: start user_info_update", 1)
        res, err = False, ""

        result = {}
        try:
            account = param["account"]
            info = param["info"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_update: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allow to change other user's info"
                elif self.caller == account and "permissionsList" in info:
                    err = "you are not allow to change your own permissionsList"
                if err != "":
                    return res, err

            res, err = self.user_info_manager.update_user_info(account, info)

            if res is False:
                return res, err
            else:
                return result, err

    def user_info_get_all(self, param):

        """
        获取用户所有信息(WARNING: ONLY ROOT CAN OWN)
        :return:
        """
        self.log.add_log("LocalCaller: start user_info_get_all", 1)

        result = {}
        try:
            accounts = param["accounts"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_get_all: Your param is incomplete", 3)
            return False, "param incomplete, attention, it's 'accounts'"
        else:
            res, err = self.user_info_manager.get_users_all_info(accounts)
            if res is False:
                return res, err
            else:
                result["usersInfo"] = res
                return result, err
                
    def user_info_get_one_multi(self, param):

        """
        获取一个用户的多个信息
        :return:
        """
        self.log.add_log("LocalCaller: start user_info_get_one_multi", 1)

        result = {}
        res, err = False, ""

        try:
            account = param["account"]
            keys = param["keys"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_get_one_multi: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allow to get other user's info"
                    return res, err

            res, err = self.user_info_manager.get_one_user_multi_info(account, keys)

            result["userInfo"] = res
            return result, err

    def user_info_get_multi_multi(self, param):

        """
        获取多个用户的多个信息(ONLY ROOT CAN OWN)
        :return:
        """
        self.log.add_log("LocalCaller: start user_info_get_multi_multi", 1)

        result = {}
        try:
            accounts = param["accounts"]
            keys = param["keys"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_get_multi_multi: Your param is incomplete", 3)
            return False, "param incomplete, caution! it's 'accounts'"
        else:
            res, err = self.user_info_manager.get_multi_users_multi_info(accounts, keys)
            result["usersInfo"] = res
            return result, err

    def user_get_permissions(self, param):

        """
        获取用户权限  其实吧...这里有个安全漏洞，用户可以获取别的用户的权限...但是吧...你获取了也没什么关系啊...
        :return:
        """
        self.log.add_log("LocalCaller: start user_get_permission", 1)

        result = {}
        try:
            account = param["account"]
        except KeyError:
            self.log.add_log("LocalCaller: user_get_permission: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            try:
                is_cache = param["isCache"]
            except KeyError:
                is_cache = True
            try:
                is_update = param["isUpdate"]
            except KeyError:
                is_update = False

            res, err = self.user_permission_manager.get_user_permissions(account, cache_to_memcached=is_cache,
                                                                         ask_update=is_update)
            if res is False:
                return False, err
            else:
                result["permissionList"] = res
                return result, err

    def user_write_permissions(self, param):

        """
        写入一个用户的权限(覆盖用户，比较用户组) (ONLY ROOT CAN OWN)
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: start user_write_permissions", 1)

        try:
            account = param["account"]
            new_permission_list = param["newPermissionList"]
        except KeyError:
            self.log.add_log("LocalCaller: user_write_permissions: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_permission_manager.write_user_permissions(account, new_permission_list)
            return res, err

    def user_edit_permissions(self, param):

        """
        编辑一个用户的权限(覆盖用户，比较用户组) (ONLY ROOT CAN OWN)
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: start user_edit_permissions", 1)

        try:
            account = param["account"]
            permissions_to_edit = param["permissionToEdit"]
        except KeyError:
            self.log.add_log("LocalCaller: user_edit_permissions: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_permission_manager.edit_user_permissions(account, permissions_to_edit)
            return res, err

    def user_group_add_users(self, param):

        """
        添加多个用户到用户组里
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: user_group_add_users", 1)

        try:
            accounts = param["accounts"]
            target_group = param["targetGroup"]
        except KeyError:
            self.log.add_log("LocalCaller: user_group_add_users: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_group_manager.add_users_into_group(accounts, target_group)
            return res, err

    def user_group_remove_users(self, param):

        """
        从用户组里移除多个用户
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: user_group_remove_users", 1)

        try:
            accounts = param["accounts"]
            target_group = param["targetGroup"]
        except KeyError:
            self.log.add_log("LocalCaller: user_group_remove_users: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_group_manager.remove_users_from_group(accounts, target_group)
            return res, err

    def user_group_move_one_to_one(self, param):

        """
        将某用户从一用户组移到另一用户组
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: user_group_move_one_to_one", 1)

        try:
            account = param["account"]
            target_group = param["targetGroup"]
        except KeyError:
            self.log.add_log("LocalCaller: user_group_move_one_to_one: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_group_manager.move_user_to_another_group(account, target_group)
            return res, err

    def user_group_add(self, param):

        """
        添加用户组
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: user_group_add", 1)

        try:
            group_name = param["groupName"]
        except KeyError:
            self.log.add_log("LocalCaller: user_group_add: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            # 支持permissionsList和fromTemple来加载，任何一个有了不能有第二个，优先permissionsList
            err_ = ""
            try:
                permissions_list = param["permissionsList"]
            except KeyError:
                try:
                    permissions_list, _ = self.user_permission_manager.get_user_permissions("", from_temple=param["fromTemple"])
                except KeyError:
                    permissions_list = None
                else:
                    if type(permissions_list) != list:
                        err_ = ", but got wrong fromTemple"
                        permissions_list = None

            res, err = self.user_group_manager.add_user_group(group_name, permissions_list=permissions_list)
            return res, err + err_

    def user_group_remove(self, param):

        """
        删除用户组
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: user_group_remove", 1)

        try:
            target_group = param["targetGroup"]
        except KeyError:
            self.log.add_log("LocalCaller: user_group_remove: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_group_manager.remove_user_group(target_group)
            return res, err
