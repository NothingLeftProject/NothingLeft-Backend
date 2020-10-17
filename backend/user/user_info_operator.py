# coding=utf-8
# author: Lan_zhijiang
# desciption: The code manage users
# date: 2020/10/17

from backend.user.user_manager import GtdUserManager


class GtdUerInfoOperator():

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

    def set_nickname(self, nickname, account=None):

        """
        设置用户昵称
        :param account: 被操作的账户
        :param nickname: 昵称
        :return: bool
        """
        account, account_info = self.reset_param(account)

        self.log.add_log("UserInfoOperator: Set %s 's nickname to %s"%account%nickname, 1)
        account_info["nickname"] = nickname

        return self.gtd_user_manager.update_user_info(account, account_info)

    def set_email(self, email, account=None):

        """

        :param email:
        :param account:
        :return:
        """
        account, account_info = self.reset_param(account)

