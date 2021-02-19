# coding=utf-8
# author: Lan_zhijiang
# desciption: stuff相关操作
# date: 2020/10/17

import json
from backend.database.mongodb import MongoDBManipulator
from backend.data.encryption import Encryption


class InboxManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.mongodb_manipulator = MongoDBManipulator(log, setting)
        self.encryption = Encryption(log, setting)

    def add_stuff(self, account, content, desc=None, tags=[], links=[], time=None, place=None, level=0, status="wait_classify"):

        """
        添加一个stuff到他个人的
        :param account: 用户名
        :param content: stuff内容
        :param desc: stuff扩展补充
        :param tags: 标签
        :param links: 链接
        :param time: 执行时间
        :param place: 执行地点
        :param level: 级别
        :param status: 状态
        :type tags: list
        :type links: list
        :return: bool, str
        """
        self.log.add_log("InboxManager: add_stuff start for user-%s" % account, 1)
        err = ""

        # is param in law
        if type(tags) != list or type(links) != list or type(level) != int:
            self.log.add_log("InboxManager: param-tags, links, level; there is a type error among them", 2)
            return False, "param-tags, links, level; there is a type error among them"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 2)
            return False, "user-%s does not exist" % account

        # generate stuff_id
        stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]
        stuff_id = self.encryption.md5(content + self.encryption.generate_random_key())
        while stuff_id in stuff_id_list:
            self.log.add_log("InboxManager: stuff_id conflict, regenerate", 1)
            stuff_id = self.encryption.md5(content + self.encryption.generate_random_key())

        # update stuff_id to database
        stuff_id_list.insert(0, stuff_id)
        if self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": 0}, {"allIdList": stuff_id_list}) is False:
            self.log.add_log("InboxManager: add stuff_id into allIdList fail, database error", 3)
            err = "add stuff_id into allIdList fail, database error, "

        # load template
        stuff_info = json.load(open("./backend/data/json/inbox_stuff_info_template.json", "r", encoding="utf-8"))
        stuff_info["_id"] = stuff_id
        stuff_info["content"] = content
        stuff_info["description"] = desc
        stuff_info["createDate"] = self.log.get_date() + "/" + self.log.get_formatted_time()
        stuff_info["stuffId"] = stuff_id
        stuff_info["tags"] = tags
        stuff_info["links"] = links
        stuff_info["time"] = time
        stuff_info["place"] = place
        stuff_info["level"] = level
        stuff_info["status"] = status

        # add to nlu understand mission
        # NLU理解stuff-content的设计：
        # 大概就是给nlu处理器content然后从中提取信息，然后信息会被自动更新到stuff_info里面（如果被更新的key是None的话）
        # 所以要给nlu.analyze_stuff的参数有：stuff_content, stuff_id, account

        # update stuff_info to database
        if self.mongodb_manipulator.add_one_document("stuff", account, stuff_info) is False:
            self.log.add_log("InboxManager: meet error when add stuff into database", 3)
            return False, err + "database error"
        else:
            self.log.add_log("InboxManager: add stuff-%s complete" % stuff_id, 1)
            return True, err + "success"

    def modify_stuff(self, account, stuff_id, info):

        """
        修改某个stuff的信息
        :param account: 被操作的用户
        :param stuff_id: stuff的id
        :param info: 要更改的信息， key:value
        :type info: dict
        :return: bool, str
        """
        self.log.add_log("InboxManager: modify user-%s 's stuff-%s info start" % account, stuff_id, 1)
        skip_keys = []

        # is param in law
        if type(info) != dict:
            self.log.add_log("InboxManager: param-info must be a dict, type error", 2)
            return False, "param-info must be a dict, type error"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 2)
            return False, "user-%s does not exist" % account

        # is stuff_id exist
        stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]
        if stuff_id not in stuff_id_list:
            self.log.add_log("InboxManager: stuff-%s does not exist in user-%s 's inbox" % stuff_id, account, 2)
            return False, "stuff-%s does not exist" % stuff_id

        # update info to database
        stuff_info = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
            ["content", "description", "createDate", "tags", "links", "time", "place", "level", "status"]
        )[0]
        need_updated_keys = list(info.keys())
        stuff_info_keys = list(info.keys())
        for key in need_updated_keys:
            if key not in stuff_info_keys:
                self.log.add_log("InboxManager: key-%s does not allow or not exist to operate, skip" % key, 2)
                skip_keys.append(key)
                continue
            stuff_info[key] = info[key]

        if self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": stuff_id}, stuff_info) is False:
            self.log.add_log("InboxManager: modify stuff info fail because of database error", 3)
            return False, "database error"
        else:
            self.log.add_log("InboxManager: modify stuff info success", 1)
            if skip_keys:
                return True, "but fail with key-%s" % skip_keys
            return True, "success"

    def get_many_stuffs(self, account, stuff_ids, get_all=False, result_type="list"):

        """
        获取多个stuff
        :param account: 用户名
        :param stuff_ids: 要获取的stuffs的id
        :param get_all: 获取全部？
        :param result_type: 返回的res的类型是什么 dict/list
        :type stuff_ids: list
        :type get_all: bool
        :return: bool, str
        """
        self.log.add_log("InboxManager: get user-%s 's many stuffs in mode-%s and get_all is %s start" % account, result_type, get_all, 1)
        skip_ids = []

        # is param in law
        if type(stuff_ids) != list and get_all is False:
            self.log.add_log("InboxManager: type error, when get_all is False, stuff_ids must be a list", 2)
            return False, "type error, when get_all is False, stuff_ids must be a list"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 2)
            return False, "user-%s does not exist" % account

        # get allIdList
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]

        # get
        if result_type == "dict":
            result = {}
            if get_all:
                if self.setting["inboxSettings"]["allowGetAllStuffsInDict"]:
                    self.log.add_log("InboxManager: get_all stuffs in dict mode, which means spend a long time!", 2)
                    for stuff_id in all_stuff_id_list:
                        result["stuff_id"] = self.mongodb_manipulator.parse_document_result(
                            self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
                            ["content", "description", "createDate", "stuffId", "tags", "links", "time", "place",
                             "level", "status"]
                        )[0]
                else:
                    self.log.add_log("InboxManager: it's not allowed to get all stuffs in dict mode", 2)
                    return False, "it's not allowed to get all stuffs in dict mode"
            else:
                for stuff_id in stuff_ids:
                    if stuff_id not in all_stuff_id_list:
                        self.log.add_log("InboxManager: can't find stuff-%s in all_stuff_id_list, skip" % stuff_id, 2)
                        skip_ids.append(stuff_ids)
                        continue

                    result["stuff_id"] = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
                        ["content", "description", "createDate", "stuffId", "tags", "links", "time", "place", "level",
                         "status"]
                    )[0]

        else:
            if get_all:
                result = list(self.mongodb_manipulator.get_document("stuff", account, mode=0))  # might error here
            else:
                result = []
                for stuff_id in stuff_ids:
                    if stuff_id not in all_stuff_id_list:
                        self.log.add_log("InboxManager: can't find stuff-%s in all_stuff_id_list, skip" % stuff_id, 2)
                        skip_ids.append(stuff_ids)
                        continue

                    result.append(
                        self.mongodb_manipulator.parse_document_result(
                            self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
                            ["content", "description", "createDate", "stuffId", "tags", "links", "time", "place", "level",
                             "status"]
                    )[0])

        if skip_ids:
            return False, "but fail with id-%s" % skip_ids
        return result, "success"



