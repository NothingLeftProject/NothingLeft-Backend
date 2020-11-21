# coding=utf-8
# author: Lan_zhijiang
# description: 用户组管理器
# date: 2020/11/1

from backend.database.memcached import MemcachedManipulator


class UserGroupManager():

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.memcached_manipulator = MemcachedManipulator(log, setting)

    def add_user_in(self, account, group_name):

        """
        添加用户到用户组中
        :param account: 要被添加的用户
        :param group_name: 目标用户组名称
        :return:
        """

    def remove_user(self, account, group_name):

        """
        移除某个用户组的用户
        :param account: 用户名
        :param group_name: 用户组名
        :return:
        """

    def move_user_to(self, account, from_group, to_group):

        """
        将某用户从一用户组移到另一用户组
        :param account: 用户名
        :param from_group: 原用户组
        :param to_group: 目标用户组
        :return:
        """

    def create_user_group(self, name):

        """
        创建用户组
        :param name: 用户组名
        :return:
        """

    def delete_user_group(self, name):

        """
        删除用户组
        :param name: 用户组名
        :return:
        """

    def edit_permission(self, param):

        """
        修改用户组权限组
        :param param: 参数
        :return:
        """

    def update_info(self, name, param):

        """
        更新用户组信息（全部）
        :param name: 用户组名
        :param param: 用户组信息
        :return:
        """

    def set_info(self, name, key, value):

        """
        设置用户组信息（个别）
        :param name: 用户组名
        :param key: 键
        :param value: 值
        :return:
        """


