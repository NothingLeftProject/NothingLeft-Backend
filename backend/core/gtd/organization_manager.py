# coding=utf-8
# author: Lan_zhijiang
# description: 组织管理器(GTD-ORGANIZE这一步骤的管理)，包括ActionChain和Project
# date: 2021/4/18

from backend.database.mongodb import MongoDBManipulator
# from backend.data.encryption import Encryption


class ReferenceManager:

    def __init__(self, base_abilities):

        self.base_abilities = base_abilities
        self.log = base_abilities.log
        self.setting = base_abilities.setting

        self.mongodb_manipulator = self.base_abilities.mongodb_manipulator
        self.encryption = self.base_abilities.encryption


class ExecutableStuffOrganizer:

    def __init__(self, base_abilities):

        self.base_abilities = base_abilities
        self.log = base_abilities.log
        self.setting = base_abilities.setting

        # self.mongodb_manipulator = self.base_abilities.mongodb_manipulator
        self.mongodb_manipulator = MongoDBManipulator(self.log, self.setting)
        self.encryption = self.base_abilities.encryption

        self.all_list_name_id_list = {
            "next": 1,
            "tracking": 2,
            "someday": 3
        }

    def add_many_stuff_to_list(self, account, stuff_ids, list_name):

        """
        添加多个stuff到清单中
        :param account:
        :param stuff_ids:
        :param list_name: 列表名称，支持id或者名字
        :type stuff_ids: list
        :type list_name: int/str
        :return:
        """
        self.log.add_log("ExecutableStuffOrganizer: add many stuffs to list-%s, user-%s" % (list_name, account), 1)
        skip_ids = []

        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("ExecutableStuffOrganizer: param-stuff_ids type error, it should be a list", 3)
            return False, "param type error"
        list_name_type = type(list_name)
        if list_name_type != int or list_name_type != str:
            self.log.add_log("ExecutableStuffOrganizer: param-list_name type error, it can be an int or str", 3)
            return False, "param type error"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("ExecutableStuffOrganizer: user-%s does not exist" % account, 3)
            return False, "user does not exist"

        # main
        # translate list_name
        if list_name_type == str:
            list_id = self.all_list_name_id_list[list_name]
        else:
            list_id = list_name

        # get list
        stuff_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("organization", account, {"_id": list_id}, 1),
            ["stuffList"]
        )[0]["stuffList"]
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]

        # add
        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list or stuff_id in stuff_list:
                self.log.add_log("ExecutableStuffOrganizer: stuff-%s does not exist or already exist, skip", 2)
                skip_ids.append(stuff_id)
                continue
            stuff_list.insert(stuff_id)

        # update
        if not self.mongodb_manipulator.update_many_documents("organization", account, {"_id": list_id}, {"stuffList": stuff_list}):
            self.log.add_log("ExecutableStuffOrganizer: can't update to database! check connection or database", 3)
            return False, "can't update to database"
        else:
            if skip_ids:
                return True, "success, but fail with %s" % skip_ids
            else:
                return True, "success"
