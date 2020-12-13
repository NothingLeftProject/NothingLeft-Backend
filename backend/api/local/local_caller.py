# coding=utf-8
# author: Lan_zhijiang
# desciption 本地api
# date: 2020/11/15

from backend.user.user_manager import UserManager


class LocalCaller:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.user_manager = UserManager(log, setting)

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
                result["status"] = "success"
                return result

