# coding=utf-8
# author: Lan_zhijiang
# description: mongodb操作器
# lastEditedDate: 2022/5/1

import pymongo
import sys

from backend.data.log import Log


class MongoDBClient:

    def __init__(self, ba, server_select="default", enable_memcache=False):

        """
        MongoDB客户端连接类，传递给MongoDBManipulator使用
        :param ba: base_abilities
        :param setting: 设置
        :param server_select: 选择服务器（配置中的名称）
        :param enable_memcache: 是否启用memcache来缓存数据
        """
        self.ba = ba
        self.parent_log = ba.parent_log
        self.log = Log(self.parent_log, "MongoDB")

        self.server_select = server_select

        self.setting = ba.setting
        self.mongodb_settings = self.setting["databaseSettings"]["mongodb"]

        self.server = None
        self.database_names_list = []
        self.collection_names_list = {}
        self.mongodb_server_address = None
        self.mongodb_server_auth = None

    def connect_to_server(self):

        """
        连接到服务器
        :return:
        """
        server = None
        try:
            mongodb_server_address = self.mongodb_settings[self.server_select]["address"]
            mongodb_server_auth = self.mongodb_settings[self.server_select]["auth"]
        except KeyError:
            self.log.add_log("Can't find mongodb_server-%s's address in the setting" % self.server_select, 3)
            sys.exit(-1)
        else:
            self.server = pymongo.MongoClient(
                host=self.mongodb_server_address["host"], port=self.mongodb_server_address["port"],
                username=self.mongodb_server_auth["username"], password=self.mongodb_server_auth["password"],
                authSource="admin",
            )

    def get_database_names_list(self):

        """
        获取所有数据库名称
        :return: list
        """
        self.database_names_list = self.server.list_database_names()
        self.log.add_log("database_names_list has been updated", 1)
        return self.database_names_list

    def get_collection_names_list(self, db_name):

        """
        获取某个数据库中所有集合名称
        :param db_name: 数据库名称
        :return:
        """
        db = self.server[db_name]

        self.collection_names_list[db_name] = db.list_collection_names()
        self.log.add_log("collection_names_list has been updated", 1)
        return self.collection_names_list[db_name]


class MongoDBManipulator:

    def __init__(self, ba, mongo_client):

        """
        MongoDB操作类，方便地集合了用法
        :param ba: base_abilities:
        :param mongo_client: MongoDBClient类
        """
        self.ba = ba
        self.parent_log = ba.parent_log
        self.log = Log(self.parent_log, "MongoDB")

        self.mongo_client = mongo_client
        self.server = mongo_client.server

        self.database_names_list = self.server.database_names_list
        self.collection_names_list = self.server.collection_names_list

    def add_database(self, db_name):

        """
        添加数据库
        :param db_name: 数据库名
        :return: bool
        """
        self.log.add_log("try add database-%s " % db_name, 1)
        try:
            self.server[db_name]
        except:
            return False
        else:
            self.server.get_database_names_list()
            return True

    def add_collection(self, db_name, coll_name):

        """
        创建集合
        :param coll_name: 集合名称
        :param db_name: 该集合要插入到的数据库
        :return:
        """
        try:
            db = self.server[db_name]
            coll = db[coll_name]
        except:
            self.log.add_log("add coll-%s into db-%s failed" % (coll_name, db_name), 3)
            return False
        else:
            self.mongo_client.get_collection_names_list(db_name)
            self.log.add_log("add coll-%s into db-%s successfully" % (coll_name, db_name), 1)
            return True

    def delete_collection(self, db_name, coll_name):

        """
        删除集合
        :param db_name: 集合所在的数据库名
        :param coll_name: 要删除的集合名
        :return: bool
        """
        try:
            db = self.server[db_name]
            db[coll_name].drop()
        except:
            self.log.add_log("delete coll-%s from db-%s failed" % (coll_name, db_name), 3)
            return False
        else:
            self.collection_names_list[db_name].remove(coll_name)
            self.log.add_log("delete coll-%s from db-%s successfully" % (coll_name, db_name), 1)
            return True

    def delete_database(self, db_name):

        """
        删除数据库
        :param db_name: 数据库名称
        :return: bool
        """
        try:
            self.server.drop_database(db_name)
        except:
            self.log.add_log("delete db-%s failed" % db_name, 3)
        else:
            self.database_names_list.remove(db_name)
            del self.collection_names_list[db_name]
            self.log.add_log("delete db-%s successfully" % db_name, 1)

    def is_database_exist(self, name, update=False):

        """
        判断某个数据库是否存在
        :param name: 数据表名称
        :param update: 是否更新
        :return: bool
        """
        if update or self.database_names_list is None:
            self.mongo_client.get_database_names_list()

        if name in self.database_names_list:
            self.log.add_log("database-%s" % name + " exist", 1)
            return True
        else:
            self.log.add_log("db_exist?: second time search start", 1)
            self.mongo_client.get_database_names_list()
            if name in self.database_names_list:
                self.log.add_log("db-%s exist" % name, 1)
                return True
            else:
                self.log.add_log("db-%s does not exist" % name, 1)
                return False

    def is_collection_exist(self, db_name, coll_name, update=False):

        """
        判断某个集合是否存在
        :param db_name: 数据库名称
        :param coll_name: 要查询的集合的名称
        :param update: 是否更新
        :return:
        """
        if update or self.collection_names_list is None:
            self.mongo_client.get_collection_names_list(db_name)

        try:
            if coll_name in self.collection_names_list[db_name]:
                self.log.add_log("collection-%s" % coll_name + " exist", 1)
                return True
        finally:
            self.log.add_log("coll_exist?: second time search start", 1)
            self.mongo_client.get_collection_names_list(db_name)
            if coll_name in self.collection_names_list[db_name]:
                self.log.add_log("collection-%s exist" % coll_name, 1)
                return True
            else:
                self.log.add_log("collection-%s does not exist" % coll_name, 1)
                return False

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
            self.log.add_log("no database named " + db_name + " or something else wrong", 3)
            return False
        else:
            try:
                coll = db[coll_name]
            except:
                self.log.add_log("no collection named " + coll_name + " or something else wrong", 3)
                return False
            else:
                try:
                    result = coll.insert_one(docu)
                except:
                    self.log.add_log("add one document failed", 3)
                    return False
                else:
                    self.log.add_log("add one document successfully", 1)
                    return result

    def add_many_documents(self, db_name, coll_name, docu_s):

        """
        添加多个文档
            在集合中添加
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param docu_s: 要插入的文档内容 list[dict, dict]
        :type docu_s: list
        :return: False or class
        """
        try:
            db = self.server[db_name]
        except:
            self.log.add_log("no database named " + db_name + " or something else wrong", 3)
            return False
        else:
            try:
                coll = db[coll_name]
            except:
                self.log.add_log("no collection named " + coll_name + " or something else wrong", 3)
                return False
            else:
                try:
                    result = coll.insert_many(docu_s)
                except:
                    self.log.add_log("add many document fail", 3)
                    return False
                else:
                    self.log.add_log("add many document success", 1)
                    return result

    def get_document(self, db_name, coll_name, query=None, mode=0):

        """
        获取某集合中的数据
        :type query: dict
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param query: 查找关键词，不指定则返回全部数据
        :param mode: 查找模式 0:全部 1:按key的值（常用于_id） 2:按key(常用于不知道_id的场景下)
        正确结果必然：[{}, {}]，一个{}就是一个docu
        :return: False/list
        """
        self.log.add_log("try to get document from " + db_name + "/" + coll_name, 1)
        if query is None:
            query = {}
        if type(query) is dict:
            try:
                db = self.server[db_name]
                coll = db[coll_name]
            except:
                self.log.add_log("get one document: something wrong", 3)
                return False
            else:
                try:
                    if mode == 0:
                        result = coll.find()
                    elif mode == 1:
                        result = coll.find(query)
                    elif mode == 2:
                        result = coll.find({}, query)
                    else:
                        self.log.add_log("mode error!", 3)
                        return False
                except:
                    self.log.add_log("get document failed", 3)
                    return False
                else:
                    return list(result)
        else:
            self.log.add_log("get one document: param query must be a dict", 3)
            return False

    def parse_document_result(self, documents, targets, debug=True):

        """
        解析搜索到的文档结果(返回包含targets中任一一个的document)
        :param documents: 查找结果
        :param targets: 查找目标
        :param debug: 是否输出哪些keys没有被找到
        :type documents: list
        :type targets: list
        :return:
        """
        self.log.add_log("parsing the documents, targets: " + str(targets), 1)
        result = []
        found_targets = []
        can_not_find_targets = []
        for target in targets:
            for document in documents:
                if target in document:
                    result.append(document)
                    found_targets.append(target)
            if target not in found_targets:
                can_not_find_targets.append(target)

        if can_not_find_targets:
            self.log.add_log("parse_result: can't find these targets in your documents: %s" % can_not_find_targets, 2)

        return result

    def generate_finding_query(self, mode, keys, values=None, mode2_mode=None):

        """
        根据模式生成查询的query
        :type keys: list
        :type values: list
        :param mode: query生成模式 1：关键词 2：要的字段
        :param mode2_mode: 模式2的模式：1：要的字段 0:不要的字段
        :param keys: 字段
        :param values: 字段对应的关键词
        :return: dict
        """
        self.log.add_log("query generate start", 1)
        query = {}
        if mode == 1:
            for index in range(0, len(keys)):
                query[keys[index]] = values[index]
        elif mode == 2:
            if mode2_mode == 1:
                for i in keys:
                    query[i] = 1
            elif mode2_mode == 0:
                for i in keys:
                    query[i] = 0
            else:
                self.log.add_log("generate finding query: if you choose mode 2, you have to fill mode2_mode correctly", 3)
                return False
        else:
            self.log.add_log("generate finding query: unknown mode", 3)
            query = False
        return query

    def update_many_documents(self, db_name, coll_name, query, values):

        """
        更新记录（文档）（多个）
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param query: 查找条件 {}
        :param values: 要修改的值（只要是一条以内的都可以） {"key": "value"}
        :return:
        """
        try:
            db = self.server[db_name]
            coll = db[coll_name]
        except:
            self.log.add_log("update_many_document: something went wrong", 3)
            return False
        else:
            values = {"$set": values}
            try:
                result = coll.update_many(query, values)
            except:
                self.log.add_log("update many document fail", 3)
                return False
            else:
                self.log.add_log("update document success. Update count: "
                                    + str(result.modified_count), 1)
                return result

    def delete_many_documents(self, db_name, coll_name, query):

        """
        删除多个文档
        :param db_name: 数据库名
        :param coll_name: 集合名
        :param query: 删除条件
        :return:
        """
        try:
            db = self.server[db_name]
            coll = db[coll_name]
        except:
            self.log.add_log("delete_many_document: something went wrong", 3)
            return False
        else:
            try:
                result = coll.delete_many(query)
            except:
                self.log.add_log("delete many document fail", 3)
                return False
            else:
                self.log.add_log("delete document success. Update count: "
                                    + str(result.deleted_count), 1)
                return result


