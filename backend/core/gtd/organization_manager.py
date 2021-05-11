# coding=utf-8
# author: Lan_zhijiang
# description: 组织管理器(GTD-ORGANIZE这一步骤的管理)，包括ActionChain和Project
# date: 2021/4/18

from backend.database.mongodb import MongoDBManipulator
# from backend.data.encryption import Encryption

import json


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

    def add_many_stuffs_to_list(self, account, stuff_ids, list_name):

        """
        添加多个stuff到清单中
        :param account:
        :param stuff_ids:
        :param list_name: 列表名称，支持id或者名字
        :type stuff_ids: list
        :type list_name: int/str
        :return: bool, str
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

    def remove_many_stuffs_from_list(self, account, stuff_ids, list_name):

        """
        从清单中删除出多个stuff
        :param account:
        :param stuff_ids:
        :param list_name: 列表名称，支持id或者名字
        :type stuff_ids: list
        :type list_name: int/str
        :return: bool, str
        """
        self.log.add_log("ExecutableStuffOrganizer: remove many stuffs to list-%s, user-%s" % (list_name, account), 1)
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

        # remove
        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list or stuff_id not in stuff_list:
                self.log.add_log("ExecutableStuffOrganizer: stuff-%s does not exist, skip", 2)
                skip_ids.append(stuff_id)
                continue
            stuff_list.remove(stuff_id)

        # update
        if not self.mongodb_manipulator.update_many_documents("organization", account, {"_id": list_id}, {"stuffList": stuff_list}):
            self.log.add_log("ExecutableStuffOrganizer: can't update to database! check connection or database", 3)
            return False, "can't update to database"
        else:
            if skip_ids:
                return True, "success, but fail with %s" % skip_ids
            else:
                return True, "success"

    # Thought
    # 通过至少一个stuff来创建一个project，可以加入更多stuff或者对一个stuff进行细化
    # 通过拖拽排列stuff，用各种逻辑关系将stuff连接起来，组成project的行动组

    # 如果不想要这么复杂的project，只是想安排一天的任务，那么可以简单的选中几个stuff创建（也可以细化）行动链，并拖拽表示先后顺序
    # project与referenceManager配合，实现附件及各种资料与行动的有机结合

    def add_project(self, account, name, stuff_ids, create_date, lots, description=None, reference_ids=[]):

        """
        创建一个项目
        :param account:
        :param stuff_ids: stuff的id list
        :param name: project名字
        :param description: project的描述
        :param reference_ids: 资料型stuff id
        :param create_date: stuff创建日期，与客户端同步 格式：datetime.date.today()/time.strftime("%H:%M:%S")
        :param lots: 最后操作时间戳-即客户端创建stuff的时间戳 str(int(time.time()))
        :type reference_ids: list
        :type stuff_ids: list
        :return: bool, project_id
        """
        self.log.add_log("ExecutableStuffOrganizer: create a project for user-%s" % account, 1)
        skip_ids = []

        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("ExecutableStuffOrganizer: param-stuff_ids type error, it should be a list", 3)
            return False, "param type error"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("ExecutableStuffOrganizer: user-%s does not exist" % account, 3)
            return False, "user does not exist"

        # main
        # generate project_id
        project_id = self.encryption.md5("project_" + name + self.encryption.generate_random_key())
        all_project_ids = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("organization", account, {"projectIds": 1}, 2),
            ["projectIds"]
        )[0]["projectIds"]
        while project_id in all_project_ids:
            self.log.add_log("OrganizationManager: project_id conflict, regenerate", 1)
            project_id = self.encryption.md5("project_" + name + self.encryption.generate_random_key())
        
        # is stuff_ids/reference_ids exist
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]
        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list:
                self.log.add_log("OrganizationManager: stuff-%s does not exist, skip", % stuff_id, 2)
                skip_ids.append(stuff_id)
                stuff_ids.remove(stuff_id)

        if reference_ids:
            for reference_id in reference_ids:
                if reference_id not in all_stuff_id_list:
                    self.log.add_log("OrganizationManager: reference-%s does not exist, skip", % reference_id, 2)
                    skip_ids.append(reference_id)
                    reference_ids.remove(reference_id)

        # load project template
        project_info = json.load(open("./backend/data/json/project_info_template.json", "r", encoding="utf-8"))
        project_info["_id"] = project_id
        project_info["projectId"] = project_id
        project_info["name"] = name
        project_info["description"] = description
        project_info["createdDate"] = create_date
        project_info["lastOperateTimeStamp"] = lots
        project_info["status"] = "just_created"
        project_info["stuffList"] = stuff_ids
        project_info["referenceList"] = reference_list

        # update database
        if not self.mongodb_manipulator.add_one_document("organization", account, project_info):
            self.log.add_log("OrganizationManager: meet database error while adding project", 3)
            return False, "database error"
        else:
            if skip_ids:
                return True, "but %s can't be add in" % skip_ids
            return True, "success"

    def delete_many_projects(self, account, project_ids):

        """
        删除多个project
        :param account: 
        :param project_ids: 要删除的project_id的list
        :type project_ids: list
        :return bool, str
        """
        self.log.add_log("OrganizationManager: delete many project in user-%s" % account, 1)
        skip_ids = []

        # is param in law
        if type(project_ids) != list:
            self.log.add_log("OrganizationManager: param-project_ids type error, it should be a list", 3)
            return False, "param type error"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("ExecutableStuffOrganizer: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # main
        all_project_ids = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("organization", account, {"projectIds": 1}, 2),
            ["projectIds"]
        )[0]["projectIds"]

        for project_id in project_ids:
            if project_id not in all_project_ids:
                self.log.add_log("OrganizationManager: project-%s does not exist, skip", 2)
                skip_ids.append(project_id)
                continue
            self.mongodb_manipulator.delete_many_documents("organization", account, {"_id": project_id})
            all_project_ids.remove(project_ids)

        # update preset_list
        self.mongodb_manipulator.update_many_documents("organization", account, {"_id": 1}, {"projectIds": project_ids})

        if skip_ids:
            return True, "but fail with proejct-%s" % skip_ids
        else:
            return True, "success"
