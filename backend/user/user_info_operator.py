# coding=utf-8
# author: Lan_zhijiang
# desciption: The code manage users
# date: 2020/10/17

from backend.user.user_manager import GtdUserManager


class GtdUerInfoManager():

    def __init__(self, account, log, setting):

        self.gtd_user_manager = GtdUserManager(log, setting)
        self.log = log
        self.setting = setting

        self.account = account
        self.account_info = self.gtd_user_manager.get_user_info([account])

    def reset_param(self, account):

        """
        将给出的参数进行判断，然后重置「减少重复代码」
        :param account: 账户名
        :return:
        """
        if account is None:
            account = self.account
            account_info = self.account_info
        else:
            account_info = self.gtd_user_manager.get_user_info([account])

        return account, account_info

    def set_info(self, key, value, account=None):

        """
        设置用户的指定信息
        :param key: 用户信息dict中要被设置的那个key
        :param value: 要设置为的value
        :param account: 账户名
        :return:
        """
        account, account_info = self.reset_param(account)

        self.log.add_log("UserInfoManager: Set " + account + " 's " + key + " to " + str(value), 1)
        account_info[key] = value
        self.account_info = account_info

        return self.gtd_user_manager.update_user_info(account, account_info)

    def get_info(self, key, account=None):

        """
        获取用户的指定信息
        :param key: 用户信息dict中要被设置的那个key
        :param value: 要设置为的value
        :param account: 账户名
        :return:
        """
        account, account_info = self.reset_param(account)

        value = account_info[key]
        self.log.add_log("UserInfoManager: Get " + account + " 's " + key + " :" + value, 1)

        return value
