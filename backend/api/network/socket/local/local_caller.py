# coding=utf-8
# author: Lan_zhijiang
# description 本地api_caller(标准化所有func的输出)
# date: 2022/5/2

from universal.log import Log


class LocalCaller:

    def __init__(self, ba, user, user_type):

        self.ba = ba
        self.parent_log = ba.parent_log
        self.log = Log(self.parent_log, "LocalCaller")
        self.setting = ba.setting

        self.user = user
        self.user_type = user_type

        if self.user == "root":
            self.not_root = False
        else:
            self.not_root = True

        self.user_manager = UserManager(self.base_abilities)
        self.user_info_manager = UserInfoManager(self.base_abilities)

        self.main = self.base_abilities.main

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
            com_code = self.com_code
        except KeyError:
            self.log.add_log("LocalCaller: user_login: Your param is incomplete!", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_manager.login(account, password, self.user_type, com_code=com_code)
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
            com_code = self.com_code
        except KeyError:
            self.log.add_log("LocalCaller: user_sign_up: Your param is incomplete!", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_manager.logout(account, self.user_type, com_code=com_code)
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
            # user_type = param["userType"]
        except KeyError:
            self.log.add_log("LocalCaller: user_sign_up: Your param is incomplete!", 3)
            return False, "param incomplete"
        else:
            res, err = self.user_manager.sign_up(account, password, self.user_type)
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

            res, err = self.user_info_manager.update_user_info(account, info, self.user_type)

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
            user_types = param["userTypes"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_get_all: Your param is incomplete", 3)
            return False, "param incomplete, attention, it's 'accounts'"
        else:
            res, err = self.user_info_manager.get_users_all_info(accounts, user_types)
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
            # user_type = param["userType"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_get_one_multi: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            if self.not_root:
                if self.caller != account:
                    err = "you are not allowed to get other user's info"
                    return res, err

            res, err = self.user_info_manager.get_one_user_multi_info(account, self.user_type, keys)
            if not res:
                result = False
            else:
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
            user_types = param["userTypes"]
        except KeyError:
            self.log.add_log("LocalCaller: user_info_get_multi_multi: Your param is incomplete", 3)
            return False, "param incomplete, caution! it's 'accounts'"
        else:
            res, err = self.user_info_manager.get_multi_users_multi_info(accounts, user_types, keys)
            if not res:
                result = False
            else:
                result["usersInfo"] = res
            return result, err

    def get_enterprise_info(self, param):

        """
        获取企业信息
        :param param
        :return
        """
        self.log.add_log("LocalCaller: start get_enterprise_info", 1)

        result = {}
        try:
            code = param["enterpriseCode"]
        except KeyError:
            self.log.add_log("LocalCaller: get_enterprise_info: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.main.get_enterprise_info(code)
            if not res:
                result = False
            else:
                result["enterpriseInfo"] = res
            return result, err

    def get_candidate_info(self, param):

        """
        获取面试者信息
        :param param
        :return
        """
        self.log.add_log("LocalCaller: start get_candidate_info", 1)

        result = {}
        try:
            code = param["candidateCode"]
        except KeyError:
            self.log.add_log("LocalCaller: get_candidate_info: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.main.get_candidate_info(code)
            if not res:
                result = False
            else:
                result["candidateInfo"] = res
            return result, err

    def get_com_info(self, param):

        """
        获取面试终端信息
        :param param
        :return
        """
        self.log.add_log("LocalCaller: start get_com_info", 1)

        result = {}
        try:
            code = param["comCode"]
        except KeyError:
            self.log.add_log("LocalCaller: get_com_info: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.main.get_com_info(code)
            if not res:
                result = False
            else:
                result["comInfo"] = res
            return result, err

    def set_apply_job(self, param):

        """
        设置面试岗位
        :param param
        :return
        """
        self.log.add_log("LocalCaller: start set_apply_job", 1)

        try:
            id_ = param["jobId"]
            account = self.caller
            com_code = self.com_code
        except KeyError:
            self.log.add_log("LocalCaller: set_apply_job: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.main.set_apply_job(id_, account, com_code)
            return res, err

    def candidate_is_interview_end(self, param):

        """
        面试者：查询面试是否结束
        :param param
        :return
        """
        self.log.add_log("LocalCaller: start candidate_is_interview_end", 1)

        try:
            account = self.caller
            com_code = self.com_code
        except KeyError:
            self.log.add_log("LocalCaller: candidate_is_interview_end: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.main.candidate_is_interview_end(account, com_code)
            return res, err

    def candidate_is_interview_started(self, param):

        """
        面试者：查询面试是否开始
        :param param
        :return
        """
        self.log.add_log("LocalCaller: start candidate_is_interview_started", 1)

        try:
            account = self.caller
            com_code = self.com_code
        except KeyError:
            self.log.add_log("LocalCaller: candidate_is_interview_started: Your param is incomplete", 3)
            return False, "param incomplete"
        else:
            res, err = self.main.candidate_is_interview_started(account, com_code)
            return res, err


