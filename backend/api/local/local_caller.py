# coding=utf-8
# author: Lan_zhijiang
# desciption 本地api
# date: 2020/11/15

from backend.user.user_manager import UserManager
from backend.user.user_info_operator import UserInfoManager
from backend.user.permission_manager import UserPermissionManager


class LocalCaller:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.user_manager = UserManager(log, setting)
        self.user_permission_manager = UserPermissionManager(log, setting)
        self.user_info_manager = UserInfoManager(log, setting)

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
            res, err = self.user_manager.login(account, password)
            if res is False:
                return False, err
            else:
                result["token"] = res


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
                return result
        
    def user_get_permissions(self, param):

        """
        获取用户权限
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
                is_update = param["isUpdate"]
            except KeyError:
                is_cache = True
                is_update = False
            
            res, err = self.user_permission_manager.get_user_permissions(account, cache_to_memcached=is_cache, ask_update=is_update)
            if res is False:
                return False, err
            else:
                result["permissionList"] = res
                return result
    
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
                return result

    def user_info_update(self, param):

        """
        更新用户信息
        :return:
        """
        self.log.add_log("LocalCaller: start user_info_update", 1)

        result = {}
        try:
            account = param["account"]
            info = param["info"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_update: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_info_manager.update_user_info(account, info)
            if res is False:
                return res, err
            else:
                return result

    def user_info_get_all(self, param):

        """
        获取用户所有信息
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
                return result
                
    def user_info_get_one_multi(self, param):

        """
        获取一个用户的多个信息
        :return:
        """
        self.log.add_log("LocalCaller: start user_info_get_one_multi", 1)

        result = {}
        try:
            account = param["account"]
            keys = param["keys"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_get_one_multi: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res = self.user_info_manager.get_one_user_multi_info(account, keys)
            result["userInfo"] = res
            return result

    def user_info_get_multi_multi(self, param):

        """
        获取多个用户的多个信息
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
            res = self.user_info_manager.get_multi_users_multi_info(accounts, keys)
            result["usersInfo"] = res
            return result
