# coding=utf-8
# author: Lan_zhijiang
# desciption: 用户信息管理器
# date: 2020/10/17

from backend.user.user_manager import UserManager
from backend.database.memcached import MemcachedManipulator


class GtdUerInfoManager():

    def __init__(self, account, log, setting):

        self.log = log
        self.setting = setting

        self.account = account
        self.account_info = self.get_user_info([account])
        self.gtd_user_manager = UserManager(log, setting)
        self.memcached_manipulator = MemcachedManipulator(log, setting)

    def update_user_info(self, account, info):

        """
        更新用户信息
        :param account: 账户名
        :param info: 要更新的信息
        :return bool
        """
        if type(info) != dict:
            self.log.add_log("UserInfoManager: Failed to update user info: info must be a dict", 3)
            return False

        user_info = self.memcached_manipulator._get("user-" + account)

        for now_key in info.keys():
            try:
                self.log.add_log("UserManager: Updating " + str(now_key) + "'s info", 1)
                user_info[now_key] = info[now_key]
            except KeyError:
                self.log.add_log("User Manager: can't find " + str(now_key) + " in user_info, skip!", 3)

        self.memcached_manipulator._replace("user-" + account, user_info)
        return True

    def get_user_info(self, accounts):

        """
        获取用户信息（可多个）
        :param accounts: 账户名 list
        :return dict
        """
        if type(accounts) != list:
            self.log.add_log("UserInfoManager: Param 'account' must be a list!", 3)
            return False

        for i in range(0, len(accounts)):
            accounts[i] = "user-" + accounts[i]

        user_info = self.memcached_manipulator._get_multi(accounts)

        for account in accounts:
            self.log.add_log("UserManager: Getting " + str(account).replace("user-", "") + "'s info", 1)
            if user_info[account] is None:
                self.log.add_log("UserManager: Can't find " + str(account).replace("user-", ""), 3)

        return user_info

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
            account_info = self.get_user_info([account])

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

        return self.update_user_info(account, account_info)

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
