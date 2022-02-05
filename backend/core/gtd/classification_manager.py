# coding=utf-8
# author: Lan_zhijiang
# description: 分类管理器 # 禁止父子分类同名
# date: 2020/10/25

import json

# from backend.database.mongodb import MongoDBManipulator
# from backend.data.encryption import Encryption


class ClassificationManager:

    def __init__(self, base_abilities):

        self.base_abilities = base_abilities
        self.log = base_abilities.log
        self.setting = base_abilities.setting

        self.mongodb_manipulator = self.base_abilities.mongodb_manipulator
        self.encryption = self.base_abilities.encryption
        # self.mongodb_manipulator = MongoDBManipulator(log, setting)
        # self.encryption = Encryption(self.log, self.setting)

        self.standard_classification_info_keys = [
            "name", "description", "stuffList", "stuffCount", "lastOperationTimeStamp",
            "classificationId", "type", "childClassificationList"
        ]

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
        判断某个cl_id是否存在
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

    def general_existence_judgment(self, account, cl_id):

        """
        通用存在判断：判断账户、分类是否存在
        :param account:
        :param cl_id:
        :return: bool, str
        """
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("ClassificationManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        if self.is_cl_id_exist(account, cl_id) is False:
            self.log.add_log("ClassificationManager: classification-%s does not exist" % cl_id, 3)
            return False, "classification-%s does not exist" % cl_id

        return True, "success"

    def add_many_stuffs(self, account, cl_id, stuff_ids):

        """
        添加多个stuffs到某个分类里
        :param account: 用户名
        :param stuff_ids:
        :param cl_id: 分类的id，父子无需分开
        :type stuff_ids: list
        :return: bool, str
        """
        self.log.add_log("ClassificationManager: add many stuffs to user-%s's cl-%s" % (account, cl_id), 1)
        skip_ids = []

        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("ClassificationManager: param-stuff_ids must be a list, type error", 3)
            return False, "ClassificationManager: param-stuff_ids must be a list, type error"

        # general existence judgement
        a, b = self.general_existence_judgment(account, cl_id)
        if a is False:
            return a, b

        # main
        cl_info = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("classification", account, {"_id": cl_id}, 1),
            self.standard_classification_info_keys
        )[0]
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]
        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list:
                self.log.add_log("ClassificationManager: stuff-%s is not exist, skip" % stuff_id, 2)
                skip_ids.append(stuff_id)
                continue
            cl_info["stuffList"].insert(stuff_id)

        # update
        if self.mongodb_manipulator.update_many_documents("classification", account, {"_id": cl_id}, {"stuffList": cl_info["stuffLIst"]}) is False:
            self.log.add_log("ClassificationManager: database error, can't add stuff into classification", 3)
            return False, "database error"
        else:
            if skip_ids:
                if skip_ids == stuff_ids:
                    return False, "all stuff_id aren't exist at all"
                else:
                    return True, "success, but fail with stuffs-%s" % skip_ids
            else:
                return True, "success"

    def remove_many_stuffs(self, account, cl_id, stuff_ids):

        """
        从分类中移除多个stuffs
        :param account: 用户名
        :param stuff_ids:
        :param cl_id: 分类的id，父子无需分开
        :return: bool, str
        """
        self.log.add_log("ClassificationManager: remove many stuffs from user-%s's cl-%s" % (account, cl_id), 1)
        skip_ids = []

        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("ClassificationManager: param-stuff_ids must be a list, type error", 3)
            return False, "ClassificationManager: param-stuff_ids must be a list, type error"

        # general existence judgement
        a, b = self.general_existence_judgment(account, cl_id)
        if a is False:
            return a, b

        # main
        cl_info = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("classification", account, {"_id": cl_id}, 1),
            self.standard_classification_info_keys
        )[0]
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]
        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list:
                self.log.add_log("ClassificationManager: stuff-%s is not exist, skip" % stuff_id, 3)
                skip_ids.append(stuff_id)
                continue
            cl_info["stuffList"].remove(stuff_id)

        # update
        if self.mongodb_manipulator.update_many_documents("classification", account, {"_id": cl_id}, {"stuffList": cl_info["stuffList"]}) is False:
            self.log.add_log("ClassificationManager: database error, can't remove stuff from classification", 3)
            return False, "database error"
        else:
            if skip_ids:
                if skip_ids == stuff_ids:
                    return False, "all stuff_id aren't exist at all"
                else:
                    return True, "success, but fail with stuffs-%s" % skip_ids
            else:
                return True, "success"

    def get_classifications_info(self, account, cl_ids, designated_keys=None, get_all=False, result_type="list"):

        """
        获取多个分类信息
        :param account: 用户名
        :param cl_ids: 要获取的分类的id列表
        :param designated_keys: 指定key
        :param get_all: 获取全部分类信息
        :param result_type: 返回数据类型 list/dict
        :type cl_ids: list
        :type designated_keys: list
        :return: list/dict/bool, str
        """
        self.log.add_log("ClassificationManager: get user-%s classifications info in mode-%s" % (account, result_type), 1)
        skip_ids = []

        # is param in law
        if type(cl_ids) != list and get_all is False:
            self.log.add_log("ClassificationManager: type error, when param-get_all is False, param-cl_ids must be a list", 3)
            return False, "ClassificationManager: type error, when get_all is False, cl_ids must be a list"
        if type(designated_keys) != list and designated_keys is not None:
            self.log.add_log("ClassificationManager: type error with param-designated_keys", 3)
            return False, "type error with param-designated_keys"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("ClassificationManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # main
        # get all cl_ids
        all_cl_ids = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("classification", account, {"_id": 0}, 1),
            ["classificationIds"]
        )[0]["classificationIds"]

        # get
        if designated_keys is None:
            designated_keys = self.standard_classification_info_keys
        else:
            for key in designated_keys:
                if key not in self.standard_classification_info_keys:
                    self.log.add_log("ClassificationManager: key-%s is not exist, remove from designated_keys" % key, 2)
                    designated_keys.remove(key)

        if result_type == "dict":
            result = {}
            if get_all:
                for cl_id in all_cl_ids:
                    cl_info = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("classification", account, {"_id": cl_id}, 1),
                        designated_keys
                    )[0]
                    result[cl_id] = cl_info
            else:
                for cl_id in cl_ids:
                    if cl_id not in all_cl_ids:
                        self.log.add_log("ClassificationManager: cl-%s is not exist, skip" % cl_id, 2)
                        skip_ids.append(cl_id)
                        continue
                    cl_info = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("classification", account, {"_id": cl_id}, 1),
                        designated_keys
                    )[0]
                    result[cl_id] = cl_info

        else:
            result = []
            if get_all:
                for cl_id in all_cl_ids:
                    cl_info = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("classification", account, {"_id": cl_id}, 1),
                        designated_keys
                    )[0]
                    result.append(cl_info)
            else:
                for cl_id in cl_ids:
                    if cl_id not in all_cl_ids:
                        self.log.add_log("ClassificationManager: cl-%s is not exist, skip" % cl_id, 2)
                        skip_ids.append(cl_id)
                        continue
                    cl_info = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("classification", account, {"_id": cl_id}, 1),
                        designated_keys
                    )[0]
                    result.append(cl_info)

        if skip_ids:
            return result, "success, but fail with cl-%s" % skip_ids
        else:
            return result, "success"

    def get_classifications_stuffs(self, account, cl_ids, start_index=None, end_index=None):

        """
        获取多个分类的stuff
        :param account: 用户名
        :param cl_ids: 分类id
        :param start_index: 开始点
        :param end_index: 结束点
        :type cl_ids: list
        :type start_index: int
        :type end_index: int
        :return: dict{cl_id: list}/bool, str
        """
        self.log.add_log("ClassificationManager: get classifications stuffs start", 1)
        skip_ids = []

        # is param in law
        if type(cl_ids) != list:
            self.log.add_log("ClassificationManager: type error, param-cl_ids must be a list", 3)
            return False, "ClassificationManager: type error, cl_ids must be a list"
        if (type(start_index) != list and start_index is not None) or (type(end_index) != list and end_index is not None):
            self.log.add_log("ClassificationManager: type error with param-start/end_index", 3)
            return False, "type error with param-start/end_index"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("ClassificationManager: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # main
        #  get all cl_ids
        all_cl_ids = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("classification", account, {"_id": 0}, 1),
            ["classificationIds"]
        )[0]["classificationIds"]
        result = {}
        for cl_id in cl_ids:
            # is cl_id exist
            if cl_id not in all_cl_ids:
                self.log.add_log("ClassificationManager: cl-%s is not exist, skip" % cl_id, 2)
                skip_ids.append(cl_id)
                continue
            stuff_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("classification", account, {"_id": cl_id}, 1),
                ["stuffList"]
            )[0]["stuffList"]
            if start_index is None:
                result[cl_id] = stuff_list
            else:
                result[cl_id] = stuff_list[start_index:end_index]

        if skip_ids:
            return result, "fail with cl-%s" % skip_ids
        else:
            return result, "success"

    def add_classification(self, account, name, lots, cl_type="parent", desc=None, p_c_id=None):

        """
        添加一个分类
        :param account: 用户名
        :param name: 分类名
        :param lots: 最后操作时间戳
        :param cl_type: 分类种类 parent/child
        :param desc: 分类描述
        :param p_c_id: 父分类id（若type为child）
        :return:
        """
        self.log.add_log("ClassificationManager: start add classification for user-%s" % account, 1)

        # is param in law
        if (cl_type == "child" and p_c_id is None) or (cl_type != "child" and cl_type !="parent"):
            self.log.add_log("ClassificationManager: if classification_type is 'child', you have to give the p_c_id", 3)
            return False, "while cl_type is 'child', you have to offer p_c_id"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("ClassificationManager: user-%s does not exist, quit" % account, 3)
            return False, "ClassificationManager: user-%s does not exist, quit" % account

        # main
        # generate classification data
        cl_id = self.encryption.md5(name)
        if cl_type == "child":
            cl_id = p_c_id + "-" + cl_id

        cl_data = json.load(open("./backend/data/json/classification_info_template.json", "r", encoding="utf-8"))
        cl_data["name"] = name
        cl_data["description"] = desc
        cl_data["lastOperationTimeStamp"] = lots
        cl_data["classificationId"] = cl_id
        cl_data["type"] = cl_type
        if cl_type == "child":  # ATTENTION: 这里可能有遗漏
            cl_data["parentId"] = p_c_id

        # update to database
        if self.mongodb_manipulator.add_one_document("classification", account, cl_data) is False:
            self.log.add_log("ClassificationManager: add classification fail because of database error", 3)
            return False, "add classification fail because of database error"
        else:
            self.log.add_log("ClassificationManager: add cl-%s success" % cl_id, 1)
            # update the preset_list
            all_cl_ids = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("classification", account, {"_id": 0}, 1),
                ["classificationIds"]
            )[0]["classificationIds"]
            all_cl_names = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("classification", account, {"_id": 0}, 1),
                ["classificationNames"]
            )[0]["classificationNames"]
            all_cl_ids.insert(cl_id)
            all_cl_names.insert(name)
            result_1 = self.mongodb_manipulator.update_many_documents("classification", account, {"_id": 0},
                                                                      {"classificationNames": all_cl_names})
            result_2 = self.mongodb_manipulator.update_many_documents("classification", account, {"_id": 0},
                                                                      {"classificationIds": all_cl_ids})
            if not result_1 or not result_2:
                self.log.add_log("ClassificationManager: fail to update preset_list", 3)
                return True, "success, but fail with update preset_list"
            return True, "success"

    def remove_classification(self, account, cl_id):

        """
        删除一个分类
        :param account: 用户名
        :param cl_id: 分类id
        :return:
        """
        self.log.add_log("ClassificationManager: remove a classification-%s of user-%s" % (cl_id, account))

        # general existence judgement
        a, b = self.general_existence_judgment(account, cl_id)
        if a is False:
            return a, b

        # main
        # remove cl_info from database
        if self.mongodb_manipulator.delete_many_documents("classification", account, {"_id": cl_id}) is False:
            self.log.add_log("ClassificationManager: remove classification fail because of database error", 3)
            return False, "database error"
        else:
            # remove cl_id from preset_list
            all_cl_ids = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("classification", account, {"_id": 0}, 1),
                ["classificationIds"]
            )[0]["classificationIds"]
            all_cl_ids.remove(cl_id)
            if self.mongodb_manipulator.update_many_documents("classification", account, {"_id": cl_id}, {"classificationIds": all_cl_ids}) is False:
                self.log.add_log("ClassificationManager: fail to update preset_list because of database error", 3)
                return False, "database error that can't update preset_list"
            else:
                return True, "success"


class ReferenceManager:

    def __init__(self, base_abilities):

        self.base_abilities = base_abilities
        self.log = base_abilities.log
        self.setting = base_abilities.setting

        self.mongodb_manipulator = self.base_abilities.mongodb_manipulator
        self.encryption = self.base_abilities.encryption
