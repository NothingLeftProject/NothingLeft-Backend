# coding=utf-8
# author: Lan_zhijiang
# description: stuff相关操作
# date: 2020/10/17

import json
import copy
from operator import itemgetter
from backend.database.mongodb import MongoDBManipulator
from backend.database.memcached import MemcachedManipulator
from backend.data.encryption import Encryption


class InboxManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting
        
        self.stuff_standard_attributes_list = [
            "content", "description", "createDate", "lastOperateTimeStamp", "stuffId", "tags",
            "links", "time", "place", "level", "status",
            "belongingClassificationId", "hasCustomAttribute", "customizedAttributes",
            "events", "eventsStatus", "isSplitAsEvent"
        ]
        self.preset_list_name = [
            "allIdList", "waitClassifyList", "waitOrganizeList", "waitExecuteList", "achievedList", "puttedOffList",
            "doneList", "failList", "cancelList"
        ]
        self.status_list = [
            "wait_classify", "wait_organize", "wait_execute", "achieved", "putted_off", "done", "fail", "cancel"
        ]
        self.list_status_mapping = {
            "allIdList": None,
            "waitClassifyList": "wait_classify",
            "waitOrganizeList": "wait_organize",
            "waitExecuteList": "wait_execute",
            "achievedList": "achieved",
            "puttedOffList": "putted_off",
            "doneList": "done",
            "failList": "fail",
            "cancelList": "cancel"
        }

        self.mongodb_manipulator = MongoDBManipulator(log, setting)
        self.memcached_manipulator = MemcachedManipulator(log, setting)
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
            self.log.add_log("InboxManager: param-tags, links, level; there is a type error among them", 3)
            return False, "param-tags, links, level; there is a type error among them"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
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
        stuff_info["lastOperateTimeStamp"] = self.log.get_time_stamp()
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
            # change preset_list
            res, err_2 = self.set_many_stuffs_status(account, [stuff_id], status)
            return True, err + "success; preset_list_change:" + err_2

    def modify_stuff(self, account, stuff_id, info):

        """
        修改某个stuff的信息
        :param account: 被操作的用户
        :param stuff_id: stuff的id
        :param info: 要更改的信息， key:value
        :type info: dict
        :return: bool, str
        """
        self.log.add_log("InboxManager: modify user-%s 's stuff-%s info start" % (account, stuff_id), 1)
        skip_keys = []

        # is param in law
        if type(info) != dict:
            self.log.add_log("InboxManager: param-info must be a dict, type error", 3)
            return False, "param-info must be a dict, type error"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # is stuff_id exist
        stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]
        if stuff_id not in stuff_id_list:
            self.log.add_log("InboxManager: stuff-%s does not exist in user-%s 's inbox" % (stuff_id, account), 2)
            return False, "stuff-%s does not exist" % stuff_id

        # main
        stuff_info = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
            self.stuff_standard_attributes_list
        )[0]
        if stuff_info["hasCustomAttribute"]:
            stuff_info = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
                self.stuff_standard_attributes_list + stuff_info["customizedAttributes"]
            )[0]

        need_updated_keys = list(info.keys())
        stuff_info_keys = list(stuff_info.keys())
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

    def add_many_stuffs_custom_attribute(self, account, stuff_ids, keys, values):

        """
        为多个stuff添加多个自定义属性
        要获取自定义属性的值则必须在get_many_stuffs中单独指定，被custom的stuff会存在标记
        :param account: 用户名
        :param stuff_ids:
        :param keys: 自定义属性名称
        :param values: 自定义属性值
        :type stuff_ids: list
        :return:
        """
        self.log.add_log("InboxManager: add many stuffs custom attribute for user-%s" % account, 1)
        skip_ids = []

        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("InboxManager: type error, stuff_ids must be a list", 3)
            return False, "type error, stuff_ids must be a list"
        if type(keys) != list:
            self.log.add_log("InboxManager: type error, keys must be a list", 3)
            return False, "type error, keys must be a list"
        if type(values) != list:
            self.log.add_log("InboxManager: type error, values must be a list", 3)
            return False, "type error, stuff_ids must be a list"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # get allIdList
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]

        # add
        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list:
                self.log.add_log("InboxManager: can't find stuff-%s in all_stuff_id_list, skip" % stuff_id, 2)
                skip_ids.append(stuff_ids)
                continue
            else:
                # get raw stuff info
                stuff_info = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
                    self.stuff_standard_attributes_list   
                )[0]
                # change hasCustomAttribute
                stuff_info["hasCustomAttribute"] = True
                for index in range(0, len(keys)):
                    stuff_info["customizedAttributes"].append(keys[index])
                    stuff_info[keys[index]] = values[index]
                if self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": stuff_id}, stuff_info) is False:
                    self.log.add_log("InboxManager: fail to add custom attributes for stuff-%s because of database error" % stuff_id, 3)
                    skip_ids.append(stuff_id)
                    continue

        if skip_ids:
            err= "fail with id-%s" % skip_ids
        else:
            err = "success"
        return True, err

    def delete_many_stuffs_custom_attribute(self, account, stuff_ids, keys, values):

        """
        为多个stuff删除多个自定义属性
        :param account: 用户名
        :param stuff_ids:
        :param keys: 自定义属性名称
        :param values: 自定义属性值
        :type stuff_ids: list
        :return:
        """
        self.log.add_log("InboxManager: delete many stuffs custom attribute form user-%s" % account, 1)
        skip_ids = []

        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("InboxManager: type error, stuff_ids must be a list", 3)
            return False, "type error, stuff_ids must be a list"
        if type(keys) != list:
            self.log.add_log("InboxManager: type error, keys must be a list", 3)
            return False, "type error, keys must be a list"
        if type(values) != list:
            self.log.add_log("InboxManager: type error, values must be a list", 3)
            return False, "type error, stuff_ids must be a list"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # get allIdList
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]

        # delete
        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list:
                self.log.add_log("InboxManager: can't find stuff-%s in all_stuff_id_list, skip" % stuff_id, 2)
                skip_ids.append(stuff_ids)
                continue
            else:
                # get raw stuff info
                stuff_info = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
                    self.stuff_standard_attributes_list
                )[0]
                # change hasCustomAttribute
                if keys == stuff_info["customizedAttributes"]:
                    stuff_info["hasCustomAttribute"] = False

                for index in range(0, len(keys)):
                    try:
                        stuff_info["customizedAttributes"].remove(keys[index])
                        del stuff_info[keys[index]]
                    except (ValueError, KeyError):
                        self.log.add_log("InboxManager: key-%s does not exist, can't delete" % keys[index], 3)
                if self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": stuff_id}, stuff_info) is False:
                    self.log.add_log("InboxManager: fail to delete custom attributes for stuff-%s because of database error" % stuff_id, 3)
                    skip_ids.append(stuff_id)
                    continue

        if skip_ids:
            err= "fail with id-%s" % skip_ids
        else:
            err = "success"
        return True, err

    def get_many_stuffs(self, account, stuff_ids, designated_keys=None, get_all=False, result_type="list"):

        """
        获取多个stuff
        :param account: 用户名
        :param stuff_ids: 要获取的stuffs的id
        :param get_all: 获取全部stuff
        :param designated_keys: 指定获取哪些信息
        :param result_type: 返回的res的类型是什么 dict/list
        :type designated_keys: list
        :type stuff_ids: list
        :type get_all: bool
        :return: bool, str
        """
        self.log.add_log("InboxManager: get user-%s 's many stuffs in mode-%s and get_all is %s start" % (account, result_type, get_all), 1)
        skip_ids, err = [], ""

        # is param in law
        if type(stuff_ids) != list and get_all is False:
            self.log.add_log("InboxManager: type error, when get_all is False, stuff_ids must be a list", 3)
            return False, "type error, when get_all is False, stuff_ids must be a list"
        if type(designated_keys) != list and designated_keys is not None:
            self.log.add_log("InboxManager: type error with param-designated_keys", 3)
            return False, "type error with param-designated_keys"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # get allIdList(一个函数内多次调用，使用这个)
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
                    for stuff_id in all_stuff_id_list: # attention: here is the all_stuff_id_list
                        stuff_info = self.mongodb_manipulator.parse_document_result(
                            self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
                            self.stuff_standard_attributes_list
                        )[0]
                        result[stuff_id] = stuff_info
                else:
                    self.log.add_log("InboxManager: it's not allowed to get all stuffs in dict mode", 2)
                    return False, "it's not allowed to get all stuffs in dict mode"
            else:
                for stuff_id in stuff_ids:
                    if stuff_id not in all_stuff_id_list:
                        self.log.add_log("InboxManager: can't find stuff-%s in all_stuff_id_list, skip" % stuff_id, 2)
                        skip_ids.append(stuff_ids)
                        continue

                    raw_stuff_info = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
                        self.stuff_standard_attributes_list
                    )[0]
                    if designated_keys is not None:
                        stuff_info = {}
                        for key in designated_keys:
                            try:
                                stuff_info[key] = raw_stuff_info[key]
                            except KeyError:
                                self.log.add_log("InboxManager: can't find key-%s when get_stuff stuff-%s, skip" % (key, stuff_id), 3)
                                err = "can't find key-%s when get_stuff stuff-%s, skip" % (key, stuff_id)
                                continue
                    else:
                        stuff_info = raw_stuff_info
                    result[stuff_id] = stuff_info

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

                    raw_stuff_info = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
                        self.stuff_standard_attributes_list
                    )[0]
                    if designated_keys is not None:
                        stuff_info = {}
                        for key in designated_keys:
                            try:
                                stuff_info[key] = raw_stuff_info[key]
                            except KeyError:
                                self.log.add_log("InboxManager: can't find key-%s when get_stuff stuff-%s, skip" % (key, stuff_id), 3)
                                err = "can't find key-%s when get_stuff stuff-%s, skip" % (key, stuff_id)
                                continue
                    else:
                        stuff_info = raw_stuff_info
                    result.append(stuff_info)

        if skip_ids:
            return True, "fail with id-%s" % skip_ids
        else:
            err = err + "success"
        return result, err

    def get_stuff_id_from_condition(self, account, condition, start_index=None, end_index=None, from_cache=False, cache=True):

        """
        根据条件来即时筛选获取stuff_id
        :param account: 账户名
        :param condition: 条件 dict: stuff_info中的key-要求value
        :param start_index: 开始index 不指定则end不作用
        :param end_index: 结束index
        :param cache: 是否缓存这次的生成结果
        :param from_cache: 是否从memcached中查找，如果有，从中查找，而不是mongodb
        :type condition: dict
        :return: bool, str
        """
        self.log.add_log("InboxManager: get stuff id list from condition in user-%s" % account, 1)
        err = "success"

        # is param in law
        if type(condition) != dict:
            self.log.add_log("InboxManager: type error with param-condition, it should be a list", 3)
            return False, "type error with param-condition, it should be a list"
        if start_index is not None and type(start_index) != str:
            self.log.add_log("InboxManager: type error with param-start_index", 3)
            return False, "type error with param-start_index"
        if end_index is not None and type(end_index) != str:
            self.log.add_log("InboxManager: type error with param-end_index", 3)
            return False, "type error with param-end_index"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # start
        condition_key = list(condition.keys())[0] # attention: 目前只支持一个条件
        result_list = []

        if from_cache:
            result_list = self.memcached_manipulator._get(condition_key+"List")
            if type(result_list) == list:
                self.log.add_log("InboxManager: get stuff_ids List from memcached success", 1)
            else:
                self.log.add_log("InboxManager: get stuff_ids List from memcached fail", 3)
                return False, "database error or condition wrong or you haven't cache it yet"
        else:
            all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
                ["allIdList"]
            )[0]["allIdList"]

            for stuff_id in all_stuff_id_list:
                try:
                    stuff_info = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
                        ["lastOperateTimeStamp", condition_key]
                    )[0]
                except IndexError:
                    pass
                else:
                    if stuff_info[condition_key] == condition[condition_key]:
                        self.log.add_log("InboxManager: find a stuff-%s match the condition, add in" % stuff_id, 0)
                        result_list.append(stuff_id)

            if cache:
                if self.memcached_manipulator._set(condition_key+"List", result_list):
                    self.log.add_log("InboxManager: result cache success", 1)
                else:
                    self.log.add_log("InboxManager: result cache fail", 3)
                    err = "result cache fail"

        if start_index is not None:
            if end_index is None:
                result_list = result_list[start_index:]
            else:
                result_list = result_list[start_index:end_index]

        return result_list, err

    def get_stuff_id_from_preset(self, account, mode, start_index=None, end_index=None):

        """
        从预设列表中获取stuff_id
        :param account: 用户名
        :param mode: 预设列表名称/id
        :param start_index: 开始index
        :param end_index: 结束index
        :return: bool, str
        """
        # is param in law
        if start_index is not None and type(start_index) != int:
            self.log.add_log("InboxManager: type error with param-start_index", 3)
            return False, "type error with param-start_index"
        if end_index is not None and type(end_index) != int:
            self.log.add_log("InboxManager: type error with param-end_index", 3)
            return False, "type error with param-end_index"

        self.log.add_log("InboxManager: get_stuff_id in mode-%s from %s to %s start" % (mode, start_index, end_index), 1)
        end_index_over = False

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # start
        if mode == "allIdList" or mode == 0:
            id_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
                ["allIdList"]
            )[0]["allIdList"]
        elif mode == "waitClassifyList" or mode == 1:
            id_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("stuff", account, {"waitClassifyList": 1}, 2),
                ["waitClassifyList"]
            )[0]["waitClassifyList"]
        elif mode == "waitOrganizeList" or mode == 2:
            id_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("stuff", account, {"waitOrganizeList": 1}, 2),
                ["waitOrganizeList"]
            )[0]["waitOrganizeList"]
        elif mode == "waitExecuteList" or mode == 3:
            id_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("stuff", account, {"waitExecuteList": 1}, 2),
                ["waitExecuteList"]
            )[0]["waitExecuteList"]
        elif mode == "achieved" or mode == 4:
            id_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("stuff", account, {"achievedList": 1}, 2),
                ["achievedList"]
            )[0]["achievedList"]
        else:
            self.log.add_log("InboxManager: unknown mode! exit", 3)
            return False, "unknown mode"

        if start_index is None:
            result = id_list
        else:
            if start_index is not None:
                if end_index is None:
                    result = id_list[start_index:]
                else:
                    if end_index > len(id_list) - 1:
                        self.log.add_log("InboxManager: end_index over the list's length", 2)
                        end_index_over = True
                    result = id_list[start_index:end_index]
            else:
                result = id_list

        if end_index_over:
            res = "end index over length"
        else:
            res = "success"
        return result, res

    def delete_many_stuffs(self, account, stuff_ids):

        """
        删除多个stuffs
        :param account: 用户名
        :param stuff_ids: 要删除的stuff的stuff_id列表
        :type stuff_ids: list
        :return: bool, str
        """
        self.log.add_log("InboxManager: delete user-%s 's many stuffs-%s" % (account, stuff_ids), 1)
        skip_ids = []
        err = ""

        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("InboxManager: type error with param-stuff_ids", 3)
            return False, "type error with param-stuff_ids"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # get allIdList
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]

        # main
        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list:
                self.log.add_log("InboxManager: stuff-%s does not exist, skip", 2)
                stuff_ids.remove(stuff_id)
                skip_ids.append(stuff_id)
                continue

            self.mongodb_manipulator.delete_many_documents("stuff", account, {"_id": stuff_id})

        # delete id in the preset_lists
        for list_id in range(0, 10):
            preset_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("stuff", account, {"_id": list_id}, 1),
                [self.preset_list_name[list_id]]
            )[0][self.preset_list_name[list_id]]

            raw_preset_list = copy.deepcopy(preset_list) # attention: to prevent raw_preset_list has the same id with preset_list

            for stuff_id in stuff_ids:
                try:
                    preset_list.remove(stuff_id)
                except ValueError:
                    self.log.add_log("InboxManager: stuff-%s is not in preset_list-%s" % (stuff_id, list_id), 0)

            if preset_list != raw_preset_list:
                self.log.add_log("InboxManager: preset_list has changed, update", 1)
                if not self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": list_id}, {self.preset_list_name[list_id]: preset_list}):
                    self.log.add_log("InboxManager: fail to update %s while deleting stuffs" % self.preset_list_name[list_id], 3)
                    err = "fail to update %s!" % self.preset_list_name[list_id]

        if skip_ids:
            if len(skip_ids) == len(stuff_ids):
                res = False
            else:
                res = True
            err = err + ", fail with id-%s" % skip_ids
        else:
            res = True
            err = err + "success"
        return res, err

    def generate_preset_stuff_list(self, account, list_name=None, update=False):

        """
        生成预设列表
        :param account: 账户名
        :param list_name: 要生成的列表的名称
        :param update: 是否更新到数据库
        :type list_name: list
        :return: bool, str
        """
        self.log.add_log("InboxManager: generate user-%s 's preset stuff list" % account, 1)
        skip_lists = []
        generated_list = []
        result_list = {}

        # is param in law
        if type(list_name) != list and list_name is not None:
            self.log.add_log("InboxManager: param-list_name type error", 3)
            return False, "param-list_name type error"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # main
        if list_name is None:
            list_name = self.preset_list_name

        for now_list in list_name:
            if list_name is not None:
                if now_list not in self.preset_list_name:
                    self.log.add_log("InboxManager: preset_list-%s does not exist", 2)
                    skip_lists.append(now_list)
                    continue
            if now_list in generated_list:
                skip_lists.append(now_list)
                self.log.add_log("InboxManager: preset_list-%s already generated just now" % list_name, 2)
                continue
            generated_list.append(now_list)

            self.log.add_log("InboxManager: generating the preset_list-%s" % now_list, 1)
            sec_stage_process_list = {}
            raw_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("stuff", account, mode=0),
                ["stuffId", "lastOperateTimeStamp", "status"]
            )

            for i in self.preset_list_name:
                if now_list == "allIdList":
                    for event in raw_list:
                        self.log.add_log("InboxManager: add stuff-%s in %s" % (event["stuffId"], now_list), 0)
                        sec_stage_process_list[int(event["lastOperateTimeStamp"])] = event["stuffId"]
                elif now_list == i:
                    for event in raw_list:
                        if event["status"] == self.list_status_mapping[i]:
                            self.log.add_log("InboxManager: add stuff-%s in %s" % (event["stuffId"], now_list), 0)
                            sec_stage_process_list[int(event["lastOperateTimeStamp"])] = event["stuffId"]

            sorted_result = sorted(sec_stage_process_list.items(), key=itemgetter(0), reverse=True)
            for i in sorted_result:
                try:
                    result_list[now_list].append(i[1])
                except KeyError:
                    result_list[now_list] = []
                    result_list[now_list].append(i[1])

        if update:
            self.log.add_log("InboxManager: update is True, update the preset list", 1)
            if result_list:
                for now_list in list(result_list.keys()):
                    self.log.add_log("InboxManager: updating preset_list-%s" % now_list, 0)
                    self.mongodb_manipulator.update_many_documents("stuff", account,
                                                                   {"_id": self.preset_list_name.index(now_list)},
                                                                   {now_list: result_list[now_list]})

        if skip_lists or not generated_list:
            err = "fail with this request list-%s which not exist or already generated just now" % skip_lists
        else:
            err = "success"

        return result_list, err

    def set_many_stuffs_status(self, account, stuff_ids, status):

        """
        设置多个stuffs的状态
        :param account: 用户名
        :param stuff_ids: 要操作的stuff的stuff_id列表
        :param status: 状态
        :type stuff_ids: list
        :return: bool, str
        """
        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("InboxManager: type error with param-stuff_ids", 3)
            return False, "type error with param-stuff_ids"
        if type(status) != str:
            self.log.add_log("InboxManager: type error with param-status", 3)
            return False, "type error with param-status"

        self.log.add_log("InboxManager: set user-%s 's many stuffs to status-%s" % (account, status), 1)
        skip_ids = []

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # main
        for s in self.status_list:
            if status == s:
                list_id = self.status_list.index(status)+1
                list_name = self.preset_list_name[list_id]
                self.log.add_log("InboxManager: add stuffs-%s to the preset_list-%s" % (stuff_ids, list_name), 0)
                preset_list = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document("stuff", account, {list_name: 1}, 2),
                    [list_name]
                )[0][list_name]
                preset_list = stuff_ids + preset_list
                self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": list_id}, {list_name: preset_list})

        for stuff_id in stuff_ids:
            if self.is_stuff_exist(account, stuff_id, verify_account=False) is False:
                self.log.add_log("InboxManager: can't find stuff-%s, skip" % stuff_id, 2)
                skip_ids.append(stuff_id)
                continue
            if self.modify_stuff(account, stuff_id, {"status": status}) is False:
                skip_ids.append(stuff_id)
                self.log.add_log("InboxManager: stuff-%s set status-%s fail" % (stuff_id, status), 3)

        if skip_ids:
            if len(skip_ids) == len(stuff_ids):
                res = False
            else:
                res = True
            err = "fail with this id-%s" % skip_ids
        else:
            res = True
            err = "success"
        return res, err

    def set_many_stuffs_level(self, account, stuff_ids, level):

        """
        设置多个stuffs的level(好像没有必要做)——放弃
        :param account: 用户名
        :param stuff_ids:
        :param level: 级别 int
        :return: bool, str
        """
        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("InboxManager: type error with param-stuff_ids", 3)
            return False, "type error with param-stuff_ids"
        if type(level) != int:
            self.log.add_log("InboxManager: type error with param-level", 3)
            return False, "type error with param-level"

        self.log.add_log("InboxManager: set user-%s 's stuffs level to %s" % account, level, 1)
        skip_ids = []

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # start
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]

    def add_events(self, account, stuff_id, start_indexes, end_indexes):

        """
        添加event（stuff中可以存在多个事件，每个事件可以有自己的status）
        :param account: 用户名
        :param stuff_id:
        :param start_indexes: event的开始位置
        :param end_indexes: event的结束位置
        :type start_indexes: list
        :type end_indexes: list
        :return: bool, str
        """
        self.log.add_log("InboxManager: add events for user-%s's stuff-%s" % account, stuff_id, 1)
        err = "success"

        # is param in law
        if type(start_indexes) != list:
            self.log.add_log("InboxManager: type error with param-start_indexes", 3)
            return False, "type error with param-start_indexes"
        if type(end_indexes) != list:
            self.log.add_log("InboxManager: type error with param-end_indexes", 3)
            return False, "type error with param-end_indexes"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # is stuff exist
        if self.is_stuff_exist(account, stuff_id, verify_account=False) is False:
            self.log.add_log("InboxManager: stuff-%s is not exist, quit" % stuff_id, 3)
            return False, "stuff-%s does not exist" % stuff_id

        # add event
        # get raw events list
        events_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
            ["events"]
        )[0]["events"]
        # generate events list
        for index in range(0, len(start_indexes)):
            try:
                event = (int(start_indexes[index])), int(end_indexes[index])
                if event in events_list:
                    self.log.add_log(
                        "InboxManager: event-%s:%s already exist, skip" % (start_indexes[index], end_indexes[index]), 2)
                    continue
                events_list.append(event)
            except IndexError:
                self.log.add_log("InboxManager: add_events: end_indexes or start_indexes is not matched, skip", 3)
                err = "end_indexes or start_indexes is not matched"
                continue
        # update
        result_1 = self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": stuff_id}, {"isSplitAsEvent": True})
        result_2 = self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": stuff_id}, {"events": events_list})

        if not result_1 or not result_2:
            self.log.add_log("InboxManager: database error while processing add_events", 3)
            err = err + ", database error"
            return False, err
        else:
            return True, err

    def remove_events(self, account, stuff_id, start_indexes, end_indexes):

        """
        删除event（stuff中可以存在多个事件，每个事件可以有自己的status）
        :param account: 用户名
        :param stuff_id:
        :param start_indexes:
        :param end_indexes:
        :type start_indexes: list
        :type end_indexes: list
        :return: bool. str
        """
        self.log.add_log("InboxManager: remove events for user-%s's stuff-%s" % account, stuff_id, 1)
        err = "success"

        # is param in law
        if type(start_indexes) != list:
            self.log.add_log("InboxManager: type error with param-start_indexes", 3)
            return False, "type error with param-start_indexes"
        if type(end_indexes) != list:
            self.log.add_log("InboxManager: type error with param-end_indexes", 3)
            return False, "type error with param-end_indexes"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # is stuff exist
        if self.is_stuff_exist(account, stuff_id, verify_account=False) is False:
            self.log.add_log("InboxManager: stuff-%s is not exist, quit" % stuff_id, 3)
            return False, "stuff-%s does not exist" % stuff_id

        # remove event
        # get events list
        events_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
            ["events"]
        )[0]["events"]
        # get events status list
        events_status_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
            ["eventsStatus"]
        )[0]["eventsStatus"]
        # remove
        for index in range(0, len(start_indexes)):
            try:
                event = (int(start_indexes[index])), int(end_indexes[index])
                if event not in events_list:
                    self.log.add_log("InboxManager: event-%s:%s does not exist, skip" % (start_indexes[index], end_indexes[index]), 2)
                    continue
                event_index = events_list.find(event)
                events_status_list.remove(events_status_list[event_index]) # 同步删除status
                events_list.remove(event)
            except IndexError:
                self.log.add_log("InboxManager: add_events: end_indexes or start_indexes is not matched, skip", 3)
                err = "end_indexes or start_indexes is not matched"
                continue
        # update
        if not events_list:
            if self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": stuff_id}, {"isSplitAsEvent": False}) is False:
                self.log.add_log("InboxManager: database error while removing events", 3)
                return False, "database error"
        result_1 = self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": stuff_id}, {"events": events_list})
        result_2 = self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": stuff_id}, {"eventsStatus": events_status_list})

        if not result_1 or not result_2:
            self.log.add_log("InboxManager: database error while removing events", 3)
            err = err + ", database error"
            return False, err
        else:
            return True, err

    def set_event_status(self, account, stuff_id, start_index, end_index, status):

        """
        设置event的状态
        :param account: 用户名
        :param stuff_id:
        :param start_index: event开始位置
        :param end_index: event结束位置
        :param status: 要设置为的状态
        :type start_index: int
        :type end_index: int
        :return: bool, str
        """
        # is param in law
        if type(start_index) != int:
            self.log.add_log("InboxManager: type error with param-start_index", 3)
            return False, "type error with param-start_index"
        if type(end_index) != int:
            self.log.add_log("InboxManager: type error with param-end_index", 3)
            return False, "type error with param-end_index"

        self.log.add_log("InboxManager: set user-%s 's event-%s:%s to status-%s" % account, start_index, end_index, status, 1)

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # is stuff exist
        if self.is_stuff_exist(account, stuff_id, verify_account=False) is False:
            self.log.add_log("InboxManager: stuff-%s is not exist, quit" % stuff_id, 3)
            return False, "stuff-%s does not exist" % stuff_id

        # set event status
        # is event exist
        events_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
            ["events"]
        )[0]["events"]
        event = (start_index, end_index)
        if event not in events_list:
            self.log.add_log("InboxManager: event-%s:%s does not exist, quit" % start_index, end_index, 3)
            return False, "event does not exist"
        else:
            # set event status
            events_status_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("stuff", account, {"_id": stuff_id}, 1),
                ["eventsStatus"]
            )[0]["eventsStatus"]
            event_index = events_list.find(event)
            events_status_list.insert(event_index, status)
            # update
            result = self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": stuff_id}, {"eventsStatus": events_status_list})
            if result:
                return True, "success"
            else:
                self.log.add_log("InboxManager: fail to set event status because of dabase error", 3)
                return False, "database error"

    def is_stuff_exist(self, account, stuff_id, verify_account=True):

        """
        判断某个stuff是否存在
        :param account: 用户名
        :param stuff_id:
        :param verify_account: 效验用户名是否存在(不在api中开放)
        :return: bool
        """
        self.log.add_log("InboxManager: is stuff-%s exist in user-%s" % (stuff_id, account), 1)

        if verify_account:
            # is account exist
            if self.mongodb_manipulator.is_collection_exist("user", account) is False:
                self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
                return False, "user-%s does not exist" % account

        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]

        if stuff_id in all_stuff_id_list:
            return True, "success"
        else:
            return False, "success"


# JUST SOME TEST HERE LOL
# yuanyihong is really angry with you now bcause of your foolish behaviour
# 袁翊闳现在是真的非常的生气，因为你那愚蠢的行为
# 也许allIdList应该放一个在Memcached里面方便快速读取
# 跳过的==给的，那res=False，爱改不改，问题不大
