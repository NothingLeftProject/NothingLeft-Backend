# coding=utf-8
# author: Lan_zhijiang
# description: 用户权限管理器
# date: 2020/11/23

from backend.database.mongodb import MongoDBManipulator


class PermissionManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting
