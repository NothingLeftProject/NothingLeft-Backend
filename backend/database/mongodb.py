# coding=utf-8
# author: Lan_zhijiang
# description: mongodb操作器
# date: 2020/11/21

import pymongo


class MongoDBManipulator():

    def __init__(self, log, setting, database_name="default"):

        self.log = log
        self.setting = setting
        self.database_name = database_name

        self.mongodb_settings = self.setting["databaseSettings"]["mongodb"]

        self.database_names_list = []
        self.collection_names_list = {}

        try:
            self.memcached_server_address = self.mongodb_settings["address"][database_name]
        except KeyError:
            self.log.add_log("MongoDB: Can't find mongodb server named: "
                             + database_name + "'s address in the settings, please check it.", 3)
        else:
            self.server = pymongo.MongoClient(
                [self.memcached_server_address]
            )

    def get_database_names_list(self):

        """
        获取所有数据库名称
        :return: list
        """
        self.database_names_list = self.server.list_database_names()
        self.log.add_log("MongoDB: database names list has been updated", 1)
        return self.database_names_list

    def is_database_exist(self, name):

        """
        判断某个数据库是否存在
        :param name: 数据表名称
        :return: bool
        """
        self.get_database_names_list()

        if name in self.collection_names_list:
            self.log.add_log("MongoDB: database " + name + " already exist", 1)
            return True
        else:
            self.log.add_log("MongoDB: database " + name + " is not exist", 1)
            return False

    def get_collection_names_list(self, db_name):

        """
        获取某个数据库中所有集合名称
        :param db_name: 数据库名称
        :return:
        """
        db = self.server[db_name]

        self.collection_names_list[db_name] = db.list_collection_names()
        self.log.add_log("MongoDB: collection names list had been updated", 1)
        return self.collection_names_list[db_name]

    def is_collection_exist(self, db_name, coll_name):

        """
        判断某个集合是否存在
        :param db_name: 数据库名称
        :param coll_name: 要查询的集合的名称
        :return:
        """
        self.get_collection_names_list(db_name)

        if coll_name in self.collection_names_list[db_name]:
            self.log.add_log("MongoDB: collection " + coll_name + " already exist", 1)
            return True
        else:
            self.log.add_log("MongoDB: collection " + coll_name + " is not exist", 1)
            return False

    def add_collection(self, db_name, coll_name):

        """
        创建集合
        :param coll_name: 集合名称
        :param db_name: 该集合要插入到的数据库
        :return:
        """
        try:
            db = self.server[db_name]
            docu = db[coll_name]
        except:
            self.log.add_log("MongoDB: add coll: " + coll_name + "to db: " + db_name + " fail", 3)
        else:
            self.log.add_log("MongoDB: add coll: " + coll_name + "to db: " + db_name + " success", 1)

    def add_one_document(self, db_name, coll_name, docu):

        """
        添加单个文档
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param docu: 要插入的文档内容 dict
        :return: False or class
        """
        try:
            db = self.server[db_name]
        except:
            self.log.add_log("MongoDB: no database named " + db_name + " or something else wrong", 3)
            return False
        else:
            try:
                coll = db[coll_name]
            except:
                self.log.add_log("MongoDB: no collection named " + coll_name + " or something else wrong", 3)
                return False
            else:
                try:
                    result = coll.insert_one(docu)
                except:
                    self.log.add_log("MongoDB: add one document fail", 3)
                    return False
                else:
                    self.log.add_log("MongoDB: add one document success", 1)
                    return result

    def add_many_document(self, db_name, coll_name, docu_s):

        """
        添加多个文档
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param docu_s: 要插入的文档内容 list[dict, dict]
        :return: False or class
        """
        try:
            db = self.server[db_name]
        except:
            self.log.add_log("MongoDB: no database named " + db_name + " or something else wrong", 3)
            return False
        else:
            try:
                coll = db[coll_name]
            except:
                self.log.add_log("MongoDB: no collection named " + coll_name + " or something else wrong", 3)
                return False
            else:
                try:
                    result = coll.insert_many(docu_s)
                except:
                    self.log.add_log("MongoDB: add many document fail", 3)
                    return False
                else:
                    self.log.add_log("MongoDB: add many document success", 1)
                    return result

    def get_document(self, db_name, coll_name, keyword=None, find_type=0):

        """
        获取某集合中的数据
        :type keyword: dict
        :type keyword: dict
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param keyword: 查找关键词，不指定则返回全部数据
        :param find_type: 查找模式
        :return: False/dict
        """
        self.log.add_log("MongoDB: try to get document from " + db_name + "/" + coll_name, 1)
        if keyword is None:
            keyword = {}
        if keyword is dict:
            try:
                db = self.server[db_name]
                coll = db[coll_name]
            except:
                self.log.add_log("MongoDB: get one: something wrong", 3)
                return False
            else:
                try:
                    if find_type == 0:
                        result = coll.find()
                    elif find_type == 1:
                        result = coll.find(keyword)
                    elif find_type == 2:
                        result = coll.find({}, keyword)
                    else:
                        self.log.add_log("MongoDB: find type error!", 3)
                        return False
                except:
                    self.log.add_log("MongoDB: get fail", 3)
                    return False
                else:
                    return result
        else:
            self.log.add_log("MongoDB: get one: param keyword must be a dict")

    def generate_keyword(self, mode, keys, values=None, mode2_mode=None):

        """
        根据模式生成查询的keyword
        :type keys: list
        :type values: list
        :param mode: keyword生成模式 1：关键词 2：要的字段
        :param mode2_mode: 模式2的模式：1：要的字段 0:不要的字段
        :param keys: 字段
        :param values: 字段对应的关键词
        :return: dict
        """
        self.log.add_log("MongoDB: keyword generate start", 1)
        keyword = {}
        if mode == 1:
            for index in range(0, len(keys)):
                keyword[keys[index]] = values[index]
        elif mode == 2:
            if mode2_mode == 1:
                for i in keys:
                    keyword[i] = 1
            elif mode2_mode == 0:
                for i in keys:
                    keyword[i] = 0
            else:
                self.log.add_log("MongoDB: generate keyword: if you choose mode 2, you have to fill mode2_mode correctly", 3)
                return False
        else:
            self.log.add_log("MongoDB: generate keyword: unknown mode", 3)
            keyword = False
        return keyword

    def update_many_document(self, db_name, coll_name, query, values):

        """
        更新记录（文档）（多个）
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param query: 查找条件
        :param values: 要修改的值（只要是一条以内的都可以）
        :return:
        """
        try:
            db = self.server[db_name]
        except:
            self.log.add_log("MongoDB: no database named " + db_name + " or something else wrong", 3)
            return False
        else:
            try:
                coll = db[coll_name]
            except:
                self.log.add_log("MongoDB: no collection named " + coll_name + " or something else wrong", 3)
                return False
            else:
                try:
                    result = coll.update_many(query, values)
                except:
                    self.log.add_log("MongoDB: add many document fail", 3)
                    return False
                else:
                    self.log.add_log("MongoDB: update value success. Update count: "
                                     + str(result.modified_count), 1)
                    return result


