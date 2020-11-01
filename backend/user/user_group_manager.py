# coding=utf-8
# author: Lan_zhijiang
# desciption: 用户组管理器
# date: 2020/11/1


class UserGroupManager():

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

    def add_user_in(self, account, group_name):

        """
        添加用户到用户组中
        :param account: 要被添加的用户
        :param group_name: 目标用户组名称
        :return:
        """