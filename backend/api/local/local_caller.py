# coding=utf-8
# author: Lan_zhijiang
# desciption 本地api
# date: 2020/11/15

from backend.user.user_manager import UserManager
from backend.user.user_info_operator import UserInfoManager
from backend.user.user_permission_mamanger import UserPermissionManager
from backend.user.user_group_manager import UserGroupManager
from backend.core.gtd.inbox_manager import InboxManager


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
        self.inbox_manager = InboxManager(log, setting)

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
                    err = "you are not allowed to change other user's info"
                elif self.caller == account and "permissionsList" in info:
                    err = "you are not allowed to change your own permissionsList"
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
                    err = "you are not allowed to get other user's info"
                    return res, err

            res, err = self.user_info_manager.get_one_user_multi_info(account, keys)

            result["userInfo"] = res
            return result, err

    def user_info_get_multi_multi(self, param):

        """ root only
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

        """ root only
        写入一个用户的权限(覆盖用户，比较用户组)
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

        """ root only
        编辑一个用户的权限(覆盖用户，比较用户组)
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

        """ root only
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

        """ root only
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

        """ root only
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

        """ root only
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

        """ root only
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

    def user_group_get_permissions(self, param):

        """
        获取用户组权限...有安全漏洞...但没关系
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: user_group_remove", 1)

        try:
            user_groups = param["userGroups"]
        except KeyError:
            self.log.add_log("LocalCaller: user_group_get_permissions: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_permission_manager.get_user_groups_permissions(user_groups)
            return res, err

    def stuff_add(self, param):

        """
        添加stuff到inbox
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: stuff_add", 1)

        try:
            account = param["account"]
            content = param["content"]
        except KeyError:
            self.log.add_log("LocalCaller: user_group_get_permissions: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to add stuff into other user's inbox"
                    return False, err

            optional_param = ["description", "tags", "links", "time", "place", "level", "status"]
            desc, tags, links, time, place, level, status = None, [], [], None, None, 0, "wait_classify"
            for key in optional_param:
                if key == "description":
                    desc = param["description"]
                elif key == "tags":
                    tags = param["tags"]
                elif key == "links":
                    links = param["links"]
                elif key == "time":
                    time = param["time"]
                elif key == "place":
                    place = param["place"]
                elif key == "level":
                    level = param["level"]
                elif key == "status":
                    status = param["status"]

            res, err = self.inbox_manager.add_stuff(account, content, desc=desc, tags=tags, links=links, time=time, place=place, level=level, status=status)
            return res, err

    def stuff_modify(self, param):

        """
        修改某个stuff的信息
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: stuff_modify", 1)

        try:
            account = param["account"]
            stuff_id = param["stuffId"]
            info = param["info"]
        except KeyError:
            self.log.add_log("LocalCaller: stuff_modify: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to mpdify other user's stuff info"
                    return False, err

            res, err = self.inbox_manager.modify_stuff(account, stuff_id, info)
            return res, err

    def stuff_get_many(self, param):

        """
        获取多个stuff
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: stuff_get_many", 1)

        try:
            account = param["account"]
            stuff_ids = param["stuffIds"]
        except KeyError:
            self.log.add_log("LocalCaller: stuff_get_many: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to get other user's stuff"
                    return False, err
            optional_param = ["designated_keys", "get_all", "result_type"]
            designated_keys, get_all, result_type = None, False, "list"
            for key in optional_param:
                if key == "description":
                    designated_keys = param["designatedKeys"]
                elif key == "get_all":
                    get_all = param["getAll"]
                elif key == "result_type":
                    result_type = param["resultType"]
            res, err = self.inbox_manager.get_many_stuffs(account, stuff_ids, designated_keys=designated_keys,
                                                          get_all=get_all, result_type=result_type)
            return res, err

    def stuff_get_id_from_condition(self, param):

        """
        通过条件来获取stuff_id
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: stuff_get_id_from_condition", 1)

        try:
            account = param["account"]
            condition = param["condition"]
        except KeyError:
            self.log.add_log("LocalCaller: stuff_get_id_from_condition: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to get other user's stuff_id"
                    return False, err

            optional_param = ["start_index", "end_index", "from_cache", "cache"]
            start_index, end_index, from_cache, cache = None, None, True, True
            for key in optional_param:
                if key == "start_index":
                    start_index = param["startIndex"]
                elif key == "end_index":
                    end_index = param["endIndex"]
                elif key == "from_cache":
                    from_cache = param["fromCache"]
                elif key == "cache":
                    cache = param["cache"]
            res, err = self.inbox_manager.get_stuff_id_from_condition(account, condition, start_index=start_index,
                                                                      end_index=end_index, from_cache=from_cache,
                                                                      cache=cache)
            return res, err

    def stuff_get_id_from_preset(self, param):

        """
        通过预设列表来获取stuff_id
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: stuff_get_id_from_preset", 1)

        try:
            account = param["account"]
            mode = param["mode"]
        except KeyError:
            self.log.add_log("LocalCaller: stuff_get_id_from_preset: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to get other user's stuff_id"
                    return False, err

            optional_param = ["start_index", "end_index"]
            start_index, end_index = None, None
            for key in optional_param:
                if key == "start_index":
                    start_index = param["startIndex"]
                elif key == "end_index":
                    end_index = param["endIndex"]
            res, err = self.inbox_manager.get_stuff_id_from_condition(account, mode, start_index=start_index,
                                                                      end_index=end_index)
            return res, err

    def stuff_delete_many(self, param):

        """
        删除多个stuff
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: stuff_delete_many", 1)

        try:
            account = param["account"]
            stuff_ids = param["stuffIds"]
        except KeyError:
            self.log.add_log("LocalCaller: stuff_delete_many: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to delete other user's stuff"
                    return False, err

            res, err = self.inbox_manager.delete_many_stuffs(account, stuff_ids)
            return res, err

    def stuff_generate_preset_list(self, param):

        """(ONLY ROOT CAN HAS)
        生成预设列表
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: stuff_generate_preset_list", 1)

        try:
            account = param["account"]
        except KeyError:
            self.log.add_log("LocalCaller: stuff_generate_preset_list: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            optional_param = ["list_name"]
            list_name = None
            for key in optional_param:
                if key == "list_name":
                    list_name = param["listName"]
            res, err = self.inbox_manager.generate_preset_stuff_list(account, list_name=list_name)
            return res, err

    def stuff_set_many_status(self, param):

        """
        设置多个stuff的状态
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: stuff_set_many_status", 1)

        try:
            account = param["account"]
            stuff_ids = param["stuffIds"]
            status = param["status"]
        except KeyError:
            self.log.add_log("LocalCaller: stuff_set_many_status: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to modify other user's stuff info"
                    return False, err

            res, err = self.inbox_manager.set_many_stuffs_status(account, stuff_ids, status)
            return res, err

    def stuff_set_many_level(self, param):

        """
        设置多个stuff的状态
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: stuff_set_many_level", 1)

        try:
            account = param["account"]
            stuff_ids = param["stuffIds"]
            level = param["level"]
        except KeyError:
            self.log.add_log("LocalCaller: stuff_set_many_level: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to modify other user's stuff info"
                    return False, err

            res, err = self.inbox_manager.set_many_stuffs_level(account, stuff_ids, level)
            return res, err

    def stuff_is_exist(self, param):

        """
        检测stuff是否存在
        :param param:
        :return:
        """
        self.log.add_log("LocalCaller: stuff_is_exist", 1)

        try:
            account = param["account"]
            stuff_id = param["stuffId"]
        except KeyError:
            self.log.add_log("LocalCaller: stuff_is_exist: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to know if the stuff in other inboxes exist"
                    return False, err

            res, err = self.inbox_manager.is_stuff_exist(account, stuff_id)
            return res, err
