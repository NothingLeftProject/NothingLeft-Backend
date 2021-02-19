# coding=utf-8
# author: Lan_zhijiang
# desciption: stuff相关操作
# date: 2020/10/17

import json
from operator import itemgetter
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
            self.log.add_log("InboxManager: type error, when get_all is False, stuff_ids must be a list", 3)
            return False, "type error, when get_all is False, stuff_ids must be a list"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
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
                            ["content", "description", "createDate", "lastOperateTimeStamp", "stuffId", "tags", "links", "time", "place",
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
                        ["content", "description", "createDate", "lastOperateTimeStamp", "stuffId", "tags", "links", "time", "place", "level",
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
                            ["content", "description", "createDate", "lastOperateTimeStamp", "stuffId", "tags", "links", "time", "place", "level",
                             "status"]
                    )[0])

        if skip_ids:
            return "fail with id-%s" % skip_ids
        else:
            err = "success"
        return result, err

    def get_stuff_id_from_condition(self, account, condition, length=None, from_cache=True, cache=True):

        """
        根据条件来即时筛选获取stuff_id
        :param account: 账户名
        :param condition: 条件 dict: stuff_info中的key-要求value
        :param length: 获取多少个，如果从memcached获取则非常有用，从mongodb则意味着要重新生成并选取
        :param cache: 是否缓存这次的生成结果
        :param from_cache: 是否从memcached中查找，如果有，从中查找，而不是mongodb
        :type condition: dict
        :return: bool, str
        """

    def get_stuff_id_from_preset(self, account, mode, start_index=None, end_index=None):

        """
        从预设列表中获取stuff_id
        :param account: 用户名
        :param mode: 预设列表名称/id
        :param start_index: 开始index
        :param end_index: 结束index
        :return: bool, str
        """
        self.log.add_log("InboxManager: get_stuff_id in mode-%s from %s to %s start" % mode, start_index, end_index, 1)
        result = []
        end_index_over = False

        # is param in law
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
            if end_index is None:
                result = id_list[start_index:]
            else:
                if end_index > len(id_list) - 1:
                    self.log.add_log("InboxManager: end_index over the list's length", 2)
                    end_index_over = True
                result = id_list[start_index:end_index]

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
        self.log.add_log("InboxManager: delete user-%s 's many stuffs" % account, 1)
        skip_ids = []

        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("InboxManager: type error with param-stuff_ids", 3)
            return False, "type error with param-stuff_ids"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # start
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]
        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list:
                self.log.add_log("InboxManager: stuff-%s does not exist, skip", 2)
                stuff_ids.remove(stuff_id)
                skip_ids.append(stuff_id)
                continue
            else:
                self.mongodb_manipulator.delete_many_documents("stuff", account, {"_id": stuff_id})

        if skip_ids:
            if len(skip_ids) == len(stuff_ids):
                res = False
            else:
                res = True
            err = "success, but fail with id-%s" % skip_ids
        else:
            res = True
            err = "success"
        return res, err

    def generate_preset_stuff_list(self, account, list_name=None):

        """
        生成预设列表
        :param account: 账户名
        :param list_name: 要生成的列表的名称
        :type list_name: list
        :return: bool, str
        """
        self.log.add_log("InboxManager: generate user-%s 's preset stuff list" % account, 1)
        skip_lists = []
        generated_list = []
        sec_stage_process_list = {}
        result_list = []

        # is param in law
        if type(list_name) != list and list_name is not None:
            self.log.add_log("InboxManager: param-list_name type error", 3)
            return False, "param-list_name type error"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # start
        all_preset_list_name = ["allIdList", "waitClassifyList", "waitOrganizeList", "waitExecuteList", "achievedList"]
        if list_name is None:
            list_name = all_preset_list_name

        for now_list in list_name:
            if now_list not in all_preset_list_name:
                self.log.add_log("InboxManager: preset_list-%s does not exist", 2)
                skip_lists.append(now_list)
                continue
            else:
                if now_list in generated_list:
                    skip_lists.append(now_list)
                    self.log.add_log("InboxManager: preset_list-%s already generated just now" % list_name, 2)
                    continue
                generated_list.append(now_list)

                raw_list = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document("stuff", account, mode=0),
                    ["stuffId", "lastOperateTimeStamp", "status"]
                )
                if now_list == "allIdList":
                    for event in raw_list:
                        sec_stage_process_list[int(event["lastOperateTimeStamp"])] = event["stuffId"]

                elif now_list == "waitClassifyList":
                    for event in raw_list:
                        if event["status"] != "wait_classify":
                            continue
                        sec_stage_process_list[int(event["lastOperateTimeStamp"])] = event["stuffId"]

                elif now_list == "waitOrganizeList":
                    for event in raw_list:
                        if event["status"] != "wait_organize":
                            continue
                        sec_stage_process_list[int(event["lastOperateTimeStamp"])] = event["stuffId"]
                elif now_list == "waitExecuteList":
                    for event in raw_list:
                        if event["status"] != "wait_execute":
                            continue
                        sec_stage_process_list[int(event["lastOperateTimeStamp"])] = event["stuffId"]
                elif now_list == "achievedList":
                    for event in raw_list:
                        if event["status"] != "achieved":
                            continue
                        sec_stage_process_list[int(event["lastOperateTimeStamp"])] = event["stuffId"]

                sorted_result = sorted(sec_stage_process_list.items(), key=itemgetter(0), reverse=True)
                for i in sorted_result:
                    result_list.append(i[1])

        if skip_lists or generated_list:
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
        self.log.add_log("InboxManager: set user-%s 's many stuffs to status-%s" % account, status, 1)
        skip_ids = []

        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("InboxManager: type error with param-stuff_ids", 3)
            return False, "type error with param-stuff_ids"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("InboxManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # start
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]

        # update preset list
        if status == "wait_classify":
            preset_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("stuff", account, {"waitClassifyList": 1}, 2),
                ["waitClassifyList"]
            )[0]["waitClassifyList"]
            preset_list = stuff_ids + preset_list  # might error here with the time order, please check it
            self.mongodb_manipulator.update_many_documents("stuff", account, {"_id": 1}, {"waitClassifyList": preset_list})
        # more to add

        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list:
                self.log.add_log("InboxManager: can't find stuff-%s, skip" % stuff_id, 2)
                skip_ids.append(stuff_id)
                continue
            if self.modify_stuff(account, stuff_id, {"status": status}) is False:
                skip_ids.append(stuff_id)
                self.log.add_log("InboxManager: stuff-%s set status-%s fail" % stuff_id, status, 3)

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


# JUST SOME TEST HERE LOL
# yuanyihong is really angry with you now bcause of your foolish behaviour
# 袁翊闳现在是真的非常的生气，因为你那愚蠢的行为
# 也许allIdList应该放一个在Memcached里面方便快速读取
# 跳过的==给的，那res=False，爱改不改，问题不大
