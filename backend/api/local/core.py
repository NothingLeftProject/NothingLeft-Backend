# coding=utf-8
# author: Lan_zhijiang
# desciption 本地api
# date: 2020/11/15

from backend.user.user_manager import UserManager


class LocalCallerCore():

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.user_manager = UserManager(log, setting)

    def user_login(self):

        """
        用户登录
        :return:
        """

    def user_sign_up(self, param):

        """
        注册
        :param param: 注册数据
        :return: bool
        """
        self.log.add_log("LocalCallerCore: start user_sign_up", 1)
        try:
            account = param["account"]
            password = param["password"]
            email = param["email"]
            user_group = param["userGroup"]
        except KeyError:
            self.log.add_log("LocalCallerCore: user_sign_up: Your param is incomplete!", 3)
            return False
        else:
            return self.user_manager.sign_up(account, password, email, user_group)

