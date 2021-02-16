# coding=utf-8
# author: Lan_zhijiang
# desciption: mysql操作类
# date: 2020/10/25

import pymysql


class MySqlManipulator():

    def __init__(self, log, setting, database_name="default"):

        self.log = log
        self.setting = setting
        self.database_name = database_name
        self.mysql_settings = self.setting["databaseSettings"]["mysql"]

        try:
            self.mysql_server_address = self.mysql_settings["address"][database_name]
        except KeyError:
            self.log.add_log("MysqlManipulator: Can't find mysql server named: "
                             + database_name + "'s address in the settings, please check it.", 3)
        else:
            self.db = pymysql.connect(host=self.mysql_server_address,
                                      user=self.mysql_settings["user"][database_name],
                                      password=self.mysql_settings["password"][database_name],
                                      port=self.mysql_settings["port"][database_name],
                                      database=self.database_name,
                                      charset="utf-8")

            self.cursor = self.db.cursor()

    def create_table(self, name):

        """
        创建表
        :return:
        """

