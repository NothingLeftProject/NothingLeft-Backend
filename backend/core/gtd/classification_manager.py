# coding=utf-8
# author: Lan_zhijiang
# description: 分类管理器
# date: 2020/10/25


class ClassifyManager():

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

    def add_many_stuffs(self, account, stuff_ids, classification_name):

        """
        添加多个stuffs到某个分类里
        :param account: 用户名
        :param stuff_ids:
        :param classification_name: 分类表名 str 或 int
        :type stuff_ids: list
        :return: bool, str
        """

    def remove_many_stuffs(self, account, stuff_ids, classification_name):

        """
        从分类中移除多个stuffs
        :param account: 用户名
        :param stuff_ids:
        :param classification_name: 分类表名 str 或 int
        :return: bool, str
        """

    def add_classification(self, account, classification_name, classification_id):

        """
        添加一个新的分类
        :param account: 用户名
        :param classification_name: 分类名 str
        :param classification_id: 分类id int
        :type classification_name: str
        :type classification_id: int
        :return: bool, str
        """

