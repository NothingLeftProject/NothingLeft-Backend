# coding=utf-8
# author: Lan_zhijiang
# description: 分类管理器 # 禁止父子分类同名
# date: 2020/10/25

from backend.database.mongodb import MongoDBManipulator
from backend.database.memcached import MemcachedManipulator
from backend.data.encryption import Encryption


class ClassificationManager():

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.mongodb_manipulator = MongoDBManipulator(log, setting)
        self.memcached_manipulator = MemcachedManipulator(log, setting)
        self.encryption = Encryption(self.log, self.setting)

    def is_cl_name_exist(self, account, cl_name):

        """
        判断某个cl_name是否存在
        :param account: 用户名
        :param cl_name:
        :return: bool
        """
        cl_name_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("classification", account, {"_id": 0}, 1),
            ["classificationNames"]
        )[0]["classificationNames"]
        if cl_name not in cl_name_list:
            return False
        else:
            return True

    def is_cl_id_exist(self, account, cl_id):

        """
        判断某个cl_name是否存在
        :param account: 用户名
        :param cl_id: 分类id
        :return: bool
        """
        cl_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("classification", account, {"_id": 0}, 1),
            ["classificationIds"]
        )[0]["classificationIds"]
        if cl_id not in cl_id_list:
            return False
        else:
            return True

    def cl_name_converter(self, account, cl_name, cl_type, cl_parent_id=None):

        """
        将分类名称转换为分类id
        :param account: 用户名
        :param cl_name: 分类名称
        :param cl_type: 分类类型（父/子）
        :param cl_parent_id: 如果是子分类，需要提交父分类的id
        :return: str/bool
        """
        self.log.add_log("ClassificationManager: converting cl_name to cl_id, cl_type-%s" % cl_type, 1)

        # is cl_name exist
        if self.is_cl_name_exist(account, cl_name) is False:
            self.log.add_log("ClassificationManager: cl_name does not exist, quit", 3)
            return False, "cl_name does not exist"

        # main
        cl_id = self.encryption.md5(cl_name)
        if cl_type == "child":
            if cl_parent_id is None:
                self.log.add_log("ClassificationManager: you have to give cl_parent_id if your cl_type is parent, quit", 3)
                return False, "you have to give cl_parent_id if your cl_type is parent"
            else:
                cl_id = cl_parent_id + cl_id
        elif cl_type == "parent":
            pass
        else:
            self.log.add_log("ClassificationManager: you have to refer the param-cl_type, quit", 3)
            return False, "you have to refer the param-cl_type"

        return cl_id, True

    def add_many_stuffs(self, account, cl_id, stuff_ids):

        """
        添加多个stuffs到某个分类里
        :param account: 用户名
        :param stuff_ids:
        :param cl_id: 分类的id，父子无需分开
        :type stuff_ids: list
        :return: bool, str
        """

    def remove_many_stuffs(self, account, cl_id, stuff_ids):

        """
        从分类中移除多个stuffs
        :param account: 用户名
        :param stuff_ids:
        :param cl_id: 分类的id，父子无需分开
        :return: bool, str
        """

    def add_classification(self, account, name, cl_type="parent", desc=None, p_c_id=None):

        """
        添加一个分类
        :param account: 用户名
        :param name: 分类名
        :param cl_type: 分类种类 parent/child
        :param desc: 分类描述
        :param p_c_id: 父分类id（若type为child）
        :return:
        """

    def remove_classification(self, account, cl_id):

        """
        删除一个分类
        :param account: 用户名
        :param cl_id: 分类id
        :return:
        """



