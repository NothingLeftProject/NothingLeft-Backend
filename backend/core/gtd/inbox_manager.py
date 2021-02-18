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
        :return:
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
            self.mongodb_manipulator.get_document("stuff", account, {"_id": 0}, 2),
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
        stuff_info = json.load(open("./backend/data/json/inbox_stuff_template.json", "r", encoding="utf-8"))
        stuff_info["content"] = content
        stuff_info["description"] = desc
        stuff_info["createDate"] = self.log.get_date() + "/" + self.log.get_formatted_time()
        stuff_info["stuff_id"] = stuff_id
        stuff_info["tags"] = tags
        stuff_info["links"] = links
        stuff_info["time"] = time
        stuff_info["place"] = place
        stuff_info["level"] = level
        stuff_info["status"] = status
        stuff_info["_id"] = stuff_id

        # update stuff_info to database
        if self.mongodb_manipulator.add_one_document("stuff", account, stuff_info) is False:
            self.log.add_log("InboxManager: meet error when add stuff into database", 3)
            return False, err + "database error"
        else:
            self.log.add_log("InboxManager: add stuff-%s complete" % stuff_id, 1)
            return True, err + "success"

