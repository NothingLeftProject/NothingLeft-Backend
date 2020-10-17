# coding=utf-8
# author: Lan_zhijiang
# desciption: inbox相关内容操作
# date: 2020/10/17

import json
import os


class GtdInboxManager():

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.inbox = self.get_inbox()

    def get_inbox(self):

        """
        获取inbox
        :return:
        """
        data_path = "./backend/data/gtd/" + self.setting["account"] + ""

    def add_stuff(self, name, tags=None, remarks=None, desc=None):

        """
        添加一个stuff到inbox中
        :param name: stuff的名称
        :param tags: 标签（不推荐填写）
        :param remarks: 备注（对后续处理可以起到提示）
        :param desc: 更加详细的描述（不推荐）
        :return: int(index)
        """

