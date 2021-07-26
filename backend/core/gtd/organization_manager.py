# coding=utf-8
# author: Lan_zhijiang
# description: 组织管理器(GTD-ORGANIZE这一步骤的管理)，包括ActionChain和Project
# date: 2021/4/18

from backend.database.mongodb import MongoDBManipulator
from backend.core.gtd.classification_manager import ClassificationManager
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
        self.classification_manager = ClassificationManager(base_abilities)

        self.all_list_name_id_list = {
            "next": 1,
            "tracking": 2,
            "someday": 3
        }

        self.cs_type_list = ["if", "prerequisite", "connective"]

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
        if type(reference_ids) != list:
            self.log.add_log("ExecutableStuffOrganizer: param-reference_ids type error, it should be a list", 3)
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
            self.log.add_log("ExecutableStuffOrganizer: project_id conflict, regenerate", 1)
            project_id = self.encryption.md5("project_" + name + self.encryption.generate_random_key())
        
        # is stuff_ids/reference_ids exist
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]
        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list:
                self.log.add_log("ExecutableStuffOrganizer: stuff-%s does not exist, skip" % stuff_id, 2)
                skip_ids.append(stuff_id)
                stuff_ids.remove(stuff_id)

        if reference_ids:
            for reference_id in reference_ids:
                if reference_id not in all_stuff_id_list:
                    self.log.add_log("ExecutableStuffOrganizer: reference-%s does not exist, skip" % reference_id, 2)
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
        project_info["referenceList"] = reference_ids

        # update database
        if not self.mongodb_manipulator.add_one_document("organization", account, project_info):
            self.log.add_log("ExecutableStuffOrganizer: meet database error while adding project", 3)
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
        self.log.add_log("ExecutableStuffOrganizer: delete many project in user-%s" % account, 1)
        skip_ids = []

        # is param in law
        if type(project_ids) != list:
            self.log.add_log("ExecutableStuffOrganizer: param-project_ids type error, it should be a list", 3)
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
                self.log.add_log("ExecutableStuffOrganizer: project-%s does not exist, skip", 2)
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

    def add_action_chain(self, account, name, lots, create_date, stuff_ids, description=None, reference_ids=[]):

        """
        添加行动链
        :param account:
        :param name: 名称
        :param lots: 客户端创建的时间戳
        :param create_date: 客户端创建时的日期
        :param stuff_ids: 
        :param description:
        :param reference_ids: 
        :type stuff_ids: list
        :type reference_ids: list
        :return bool, str
        """
        self.log.add_log("ExecutableStuffOrganizer: add action chain for user-%s " % account, 1)
        skip_ids = []

        # is param in law
        if type(stuff_ids) != list:
            self.log.add_log("ExecutableStuffOrganizer: param-stuff_ids type error, it should be a list", 3)
            return False, "param type error"
        if type(reference_ids) != list:
            self.log.add_log("ExecutableStuffOrganizer: param-reference_ids type error, it should be a list", 3)
            return False, "param type error"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("ExecutableStuffOrganizer: user-%s does not exist" % account, 3)
            return False, "user does not exist"
        
        # is stuff_ids/reference_ids exist
        all_stuff_id_list = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
            ["allIdList"]
        )[0]["allIdList"]
        for stuff_id in stuff_ids:
            if stuff_id not in all_stuff_id_list:
                self.log.add_log("ExecutableStuffOrganizer: stuff-%s does not exist, skip" % stuff_id, 2)
                skip_ids.append(stuff_id)
                stuff_ids.remove(stuff_id)

        if reference_ids:
            for reference_id in reference_ids:
                if reference_id not in all_stuff_id_list:
                    self.log.add_log("ExecutableStuffOrganizer: reference-%s does not exist, skip" % reference_id, 2)
                    skip_ids.append(reference_id)
                    reference_ids.remove(reference_id)

        # main
        # generate chain_id
        chain_id = self.encryption.md5("chain_" + name + self.encryption.generate_random_key())
        all_chain_ids = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("organization", account, {"actionChainIds": 1}, 2),
            ["actionChainIds"]
        )[0]["actionChainIds"]
        while chain_id in all_chain_ids:
            self.log.add_log("ExecutableStuffOrganizer: chain_id conflict, regenerate", 1)
            chain_id = self.encryption.md5("chain_" + name + self.encryption.generate_random_key())

        # load action chain info
        chain_info = json.load(open("./backend/data/json/action_chain_info_template.json", "r", encoding="utf-8"))
        chain_info["name"] = name
        chain_info["description"] = description
        chain_info["lastOperateTimeStamp"] = lots
        chain_info["createDate"] = create_date
        chain_info["_id"] = chain_id
        chain_info["chainId"] = chain_id
        chain_info["status"] = "just_create"
        chain_info["stuffList"] = stuff_ids
        chain_info["referenceList"] = reference_ids

        # update to database
        if not self.mongodb_manipulator.add_one_document("organization", account, chain_info):
            self.log.add_log("ExecutableStuffOrganizer: meet database error while adding action chain", 3)
            return False, "database error"
        else:
            if skip_ids:
                return True, "but %s can't be add in" % skip_ids
            return True, "success"

    def delete_many_action_chains(self, account, chain_ids):

        """
        删除多个行动链
        :param account: 
        :param chain_ids: 要删除的行动链id
        :return bool, str
        """
        self.log.add_log("ExecutableStuffOrganizer: delete action chain for user-%s" % account, 1)
        skip_ids = []

        # is param in law
        if type(chain_ids) != list:
            self.log.add_log("ExecutableStuffOrganizer: param-chain_ids type error, it should be a list", 3)
            return False, "param type error"

        # is account exist
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("ExecutableStuffOrganizer: user-%s does not exist" % account, 3)
            return False, "user-%s does not exist" % account

        # main
        all_chain_ids = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("organization", account, {"actionChainIds": 1}, 2),
            ["actionChainIds"]
        )[0]["actionChainIds"]
        for chain_id in chain_ids:
            if chain_id not in all_chain_ids:
                self.log.add_log("ExecutableStuffOrganizer: chain-%s is not exist, skip" % chain_id, 2)
                skip_ids.append(chain_id)
                continue
            self.mongodb_manipulator.delete_many_documents("organization", account, {"_id": chain_id})
            all_chain_ids.remove(chain_id)
        
        if not self.mongodb_manipulator.update_many_documents("organization", account, {"_id": 2}, {"chainIds": all_chain_ids}):
            self.log.add_log("ExecutableStuffOrganizer：database error, can't update preset_list", 3)
            return False, "database error"
        
        if skip_ids:
            return True, "but fail with %s" % skip_ids
        return True, "success"

    def modify_project_info(self, account, project_id, mode, param):

        """
        修改project的信息
        :param account: 用户名
        :param project_id: projectid
        :param mode: 操作 1：modify_stu_ref_list 2: modify_chunk_list 3: modify_cs_list 4: modify_chain_list
        :param param: 参数
        :type param: dict
        :type mode: str/int
        :return: bool/str
        """
        self.log.add_log("ExecutableStuffOrganizer: modify_project_info in mode-%s" % mode, 1)

        # is param in law
        if type(mode) != int or type(mode) != str:
            self.log.add_log("ExecutableStuffOrganizer: param-mode type error, it should be a int or str", 3)
            return False, "param-mode type error"
        if type(param) != dict:
            self.log.add_log("ExecutableStuffOrganizer: param-param type error, it should be a dict", 3)
            return False, "param-param type error"

        # is account exist
        if not self.mongodb_manipulator.is_collection_exist("user", account):
            self.log.add_log("ExecutableStuffOrganizer: user-%s does not exist, quit" % account, 3)
            return False, "user-%s does not exist" % account

        # main
        # is project exist
        all_chain_ids = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("organization", account, {"projectIds": 1}, 2),
            ["projectIds"]
        )[0]["projectIds"]
        if project_id not in all_chain_ids:
            self.log.add_log("ExecutableStuffOrganizer: project-%s does not exist, quit" % project_id, 3)
            return False, "project-%s does not exist" % project_id

        # init func
        def modify_stuff_reference_list(type_, operation, ids, mandatory_operation):

            """
            修改stuff/reference列表内容
            :param type_: 是修改stuff还是reference
            :param operation: 操作：添加/删除
            :param ids: 要添加/删除的
            :param mandatory_operation: 是否强制操作
            :type mandatory_operation: bool
            :return: bool, str
            """
            self.log.add_log("ExecutableStuffOrganizer: modify_stuff_reference_list: %s %s stuff reference list" % (operation, type_), 1)
            if type(ids) != list:
                self.log.add_log("ExecutableStuffOrganizer: type error, param-ids should be a list", 3)
                return False, "param-ids type error"
            if type(mandatory_operation) != bool:
                self.log.add_log("ExecutableStuffOrganizer: type error, param-mandatory_operation should be a bool", 1)
                return False, "param-mandatory_operation type error"

            # init the type_
            if type_ == "stuff":
                type_ = "stuffList"
                all_ids_list = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document("stuff", account, {"allIdList": 1}, 2),
                    ["allIdList"]
                )[0]["allIdList"]
            elif type_ == "reference":
                type_ = "referenceList"
                re_cl_id = self.classification_manager.cl_name_converter(account, type_, "parent")
                all_ids_list = self.classification_manager.get_classifications_stuffs(account, [re_cl_id])[re_cl_id]
            else:
                self.log.add_log("ExecutableStuffOrganizer: unknown value of param-type_, exit", 3)
                return False, "unknown value of param-type_"

            project_info = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("organization", account, {"_id": project_id}, 1),
                ["projectId"]
            )[0]
            now_operation_list = project_info[type_]
            if operation == "add":
                # append ids into the list
                for the_id in ids:
                    # step.1 is the id exist
                    if the_id not in all_ids_list:
                        self.log.add_log("ExecutableStuffOrganizer: %s does not exist, skip" % the_id, 2)
                        continue
                    # step.2 is the id already exist in the list
                    if the_id in now_operation_list:
                        self.log.add_log("ExecutableStuffOrganizer: %s does already exist in the %s list, skip" % (the_id, type_), 2)
                        continue
                    # step.3 append
                    now_operation_list.append(the_id)

            elif operation == "delete":
                # delete ids from the list
                for the_id in ids:
                    # step.1 is the id exist in the list
                    if the_id in now_operation_list:
                        self.log.add_log("ExecutableStuffOrganizer: %s does already exist in the %s list, skip" % (the_id, type_), 2)
                        continue
                    # step.2 is the id in using
                    using = False
                    index_id = project_info[type_].index(the_id)
                    for chunk_id in project_info["chunkIdList"]:
                        chunk_info = project_info["chunkList"][chunk_id]
                        chunk_type = chunk_info["type"]
                        if chunk_type == 0:
                            if index_id == chunk_info["content"]["stuffId"]:
                                using = True
                                break
                        elif chunk_type == 1:
                            if index_id == chunk_info["content"]["referenceId"]:
                                using = True
                                break
                        elif chunk_type == 2:
                            if index_id in chunk_info["content"]["stuffIdList"]:
                                using = True
                                break
                    if using:
                        if mandatory_operation:
                            self.log.add_log("ExecutableStuffOrganizer: %s-%s is in use, mandatory operation will make it removed in workflow" % (type_, the_id), 2)
                            # step.3 mandatory delete
                            now_operation_list.remove(the_id)
                        else:
                            self.log.add_log("ExecutableStuffOrganizer: %s-%s is in use, ask for confirmation", 2)
                            return False, {"operation": "ask",
                                           "case": "001"}
                    else:
                        # step.3 delete
                        now_operation_list.remove(the_id)
            else:
                self.log.add_log("ExecutableStuffOrganizer: unknown operation-%s, exit" % operation, 3)
                return False, "unknown operation"

            # step.5 update to database
            if not self.mongodb_manipulator.update_many_documents("organization", account, {"_id": project_id}, {type_: now_operation_list}):
                self.log.add_log("ExecutableStuffOrganizer: database error, can't update the changes to database", 3)
                return False, "database error, can't update the changes to database"
            else:
                return True, "success"

        def modify_chunk_list(operation, ids=None, info=None):

            """
            修改chunk列表
            :param operation: 操作：添加/删除
            :param ids: 删除时填写
            :param info: 添加时填写
            :type info: list[dict, dict]
            :type ids: list
            :return: bool, str
            """
            self.log.add_log("ExecutableStuffOrganizer: modify_chunk_list: %s chunks" % operation, 1)

            project_info = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("organization", account, {"_id": project_id}, 1),
                ["projectId"]
            )[0]

            # is param in law
            if operation == "add":
                if type(info) != list or type(info[0]) != dict:
                    self.log.add_log("ExecutableStuffOrganizer: type error, in the operation-add, param-info must be a list and its elements must be dict", 3)
                    return False, "type error, operation-add requires param-info in type-list and its elements in type-dict"

                chunk_info_template_raw = json.load(open("./backend/data/json/project_chunk_info_template.json", "r", encoding="utf-8"))
                for raw_info in info:
                    chunk_info_template = chunk_info_template_raw
                    # add new chunks
                    # step.1 load params
                    chunk_type = raw_info["type"]
                    chunk_info_template["type"] = chunk_type
                    if "cs:" in raw_info["last"] or "chunk:" in raw_info["last"]:
                        chunk_info_template["last"] = raw_info["last"]
                    else:
                        self.log.add_log("ExecutableStuffOrganizer: wrong format of param-'last', skip", 3)
                        continue
                    if "cs:" in raw_info["next"] or "chunk:" in raw_info["next"]:
                        chunk_info_template["next"] = raw_info["next"]
                    else:
                        self.log.add_log("ExecutableStuffOrganizer: wrong format of param-'next', skip", 3)
                        continue
                    try:
                        chunk_info_template["relateTo"] = raw_info["relateTo"]
                    except KeyError:
                        pass

                    # step.2 is content completed
                    content = raw_info["content"]
                    if chunk_type == 0:
                        check_event = ["stuffId"]
                    elif chunk_type == 1:
                        check_event = ["referenceId"]
                    elif chunk_type == 2:
                        check_event = ["stuffIdList", "csId"]
                    elif chunk_type == 3:
                        check_event = ["csId", "chunkIdList"]
                    else:
                        self.log.add_log("ExecutableStuffOrganizer: chunk_type-%s does not supported, exit" % chunk_type, 3)
                        return False, "unknown value of chunk_type"
                    for event in check_event:
                        try:
                            content[event]
                        except KeyError:
                            self.log.add_log("ExecutableStuffOrganizer: in the chunk_type-%s, %s is necessary in the param-content" % (chunk_type, event), 3)
                            return False, "chunk_content does not completed"
                    chunk_info_template["content"] = content

                    # step.3 generate chunk id
                    project_info["chunkCounts"] += 1
                    chunk_id = self.encryption.md5(project_info["chunkCounts"] + self.encryption.generate_random_key())
                    while chunk_id in project_info["chunkIdList"]:
                        chunk_id = self.encryption.md5(project_info["chunkCounts"] + self.encryption.generate_random_key())
                    chunk_info_template["chunkId"] = chunk_id

                    project_info["chunkList"][chunk_id] = chunk_info_template
                    project_info["chunkIdList"].append(chunk_id)

            elif operation == "delete":
                if type(ids) != list:
                    self.log.add_log("ExecutableStuffOrganizer: type error, param-ids must be a list while operation-delete, exit", 3)
                    return False, "type error, param-ids must be a list"

                # delete chunks
                chunk_id_list = project_info["chunkIdList"]
                for chunk_id in ids:
                    # step.1 is chunk_id exist
                    if chunk_id not in chunk_id_list:
                        self.log.add_log("ExecutableStuffOrganizer: chunk-%s does not exist, skip" % chunk_id, 2)
                        continue

                    # step.2 is chunk in use ATTENTION: 虽然此处使用last/next_chunk_id，但不一定就是chunk的id了，
                    now_chunk_info = project_info["chunkList"][chunk_id]
                    if now_chunk_info["last"] is None and now_chunk_info["next"] is not None:
                        # using mode1: startup
                        self.log.add_log("ExecutableStuffOrganizer: chunk-%s is in use(mode1), delete will cause autofix" % chunk_id, 2)

                        next_chunk_id = now_chunk_info["next"]
                        project_info["chunkList"][next_chunk_id]["last"] = None
                    elif now_chunk_info["last"] is not None and now_chunk_info["next"] is None:
                        # using mode2: ending
                        self.log.add_log("ExecutableStuffOrganizer: chunk-%s is in use(mode2), delete will cause autofix" % chunk_id, 2)

                        last_chunk_id = now_chunk_info["last"]
                        project_info["chunkList"][last_chunk_id]["next"] = None
                    elif now_chunk_info["last"] is not None and now_chunk_info["next"] is not None:
                        # using mode3: normal
                        self.log.add_log("ExecutableStuffOrganizer: chunk-%s is in use(mode3), delete will cause autofix" % chunk_id, 2)

                        last_chunk_id = now_chunk_info["last"]
                        next_chunk_id = now_chunk_info["next"]
                        project_info["chunkList"][next_chunk_id]["last"] = last_chunk_id
                        project_info["chunkList"][last_chunk_id]["next"] = next_chunk_id

                    # step.3 delete chunk in normal
                    del project_info["chunkList"][chunk_id]
                    project_info["chunkIdList"].remove(chunk_id)
                    project_info["chunkCount"] -= 1

            else:
                self.log.add_log("ExecutableStuffOrganizer: unknown operation-%s, exit" % operation, 3)
                return False, "unknown operation-%s" % operation

            # step.4 update to database
            if not self.mongodb_manipulator.update_many_documents("organization", account, {"_id": project_id},
                                                           {"chunkList": project_info["chunkList"],
                                                            "chunkCount": project_info["chunkCount"],
                                                            "chunkIdList": project_info["chunkIdList"]
                                                            }):
                self.log.add_log("ExecutableStuffOrganizer: database error, cannot update", 3)
                return False, "database error"
            else:
                return True, "success"

        def modify_cs_list(operation, ids=None, info=None):

            """
            修改connection_structure列表
            :param operation: 操作：添加/删除
            :param ids: 删除时填写
            :param info: 添加时填写
            :type info: list[dict, dict]
            :type ids: list
            :return: bool, str
            """
            self.log.add_log("ExecutableStuffOrganizer: modify_cs_list: %s connective structure" % operation, 1)

            project_info = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("organization", account, {"_id": project_id}, 1),
                ["projectId"]
            )[0]

            if operation == "add":
                if type(info) != list:
                    self.log.add_log("ExecutableStuffOrganizer: type error, in the operation-add, param-info must be a list and its elements must be dict", 3)
                    return False, "type error, operation-add requires param-info in type-list and its elements in type-dict"

                # add cs
                cs_info_template_raw = json.load(open("./backend/data/json/project_cs_template.json", "r", encoding="utf-8"))
                for cs_info in info:
                    cs_info_template = cs_info_template_raw
                    # step.1-1 check basic params
                    if cs_info["type"] not in self.cs_type_list:
                        self.log.add_log("ExecutableStuffOrganizer: cs_type-%s does not supported, skip" % cs_info["type"], 3)
                        continue
                    if "chunk" not in cs_info["last"] and "chain" not in cs_info["last"]:
                        self.log.add_log("ExecutableStuffOrganizer: cs can only connect to chunk or chain, skip", 3)
                        continue

                    # step.2 load basic params
                    cs_info_template["type"] = cs_info["type"]
                    cs_info_template["last"] = cs_info["last"]
                    cs_info_template["next"] = cs_info["next"]
                    try:
                        cs_info_template["param"] = cs_info["param"]
                    except KeyError:
                        cs_info_template["param"] = {}

                    # step.3 generate cs_id
                    project_info["connectiveStructureCount"] += 1
                    cs_id = self.encryption.md5(project_info["connectiveStructureCount"] + self.encryption.generate_random_key())
                    while cs_id in project_info["connectiveStructureIdList"]:
                        cs_id = self.encryption.md5(project_info["connectiveStructureCount"] + self.encryption.generate_random_key())
                    cs_info_template["csId"] = cs_id

                    project_info["connectiveStructureIdList"].append(cs_id)
                    project_info["connectiveStructureList"][cs_id] = cs_info_template
            elif operation == "delete":
                if type(ids) != list:
                    self.log.add_log("ExecutableStuffOrganizer: type error, param-ids must be a list while operation-delete, exit", 3)
                    return False, "type error, param-ids must be a list"

                # delete cs
                cs_id_list = project_info["connectiveStructureIdList"]
                for cs_id in ids:
                    # step.1 is cs_id exist
                    if cs_id not in cs_id_list:
                        self.log.add_log("ExecutableStuffOrganizer: cs-%s does not exist, skip" % cs_id, 3)
                        continue

                    # step.2 is cs in use
                    now_cs_info = project_info["connectiveStructureList"][cs_id]
                    if now_cs_info["last"] is None and now_cs_info["next"] is not None:
                        # using mode1: startup
                        self.log.add_log("ExecutableStuffOrganizer: cs-%s is in use(mode1), delete will cause autofix" % cs_id, 2)

                        next_cs_id = now_cs_info["next"]
                        project_info["connectiveStructureList"][next_cs_id]["last"] = None
                    elif now_cs_info["last"] is not None and now_cs_info["next"] is None:
                        # using mode2: ending
                        self.log.add_log("ExecutableStuffOrganizer: cs-%s is in use(mode2), delete will cause autofix" % cs_id, 2)

                        last_cs_id = now_cs_info["last"]
                        project_info["connectiveStructureList"][last_cs_id]["next"] = None
                    elif now_cs_info["last"] is not None and now_cs_info["next"] is not None:
                        # using mode3: normal
                        self.log.add_log("ExecutableStuffOrganizer: cs-%s is in use(mode3), delete will cause autofix" % cs_id, 2)

                        last_cs_id = now_cs_info["last"]
                        next_cs_id = now_cs_info["next"]
                        project_info["connectiveStructureList"][next_cs_id]["last"] = last_cs_id
                        project_info["connectiveStructureList"][last_cs_id]["next"] = next_cs_id

                    # step.3 delete cs in normal
                    del project_info["connectiveStructureList"][cs_id]
                    project_info["connectiveStructureIdList"].remove(cs_id)
                    project_info["connectiveStructureCount"] -= 1

            else:
                self.log.add_log("ExecutableStuffOrganizer: unknown operation-%s, exit" % operation, 3)
                return False, "unknown operation-%s" % operation

            # step.4 update to database
            if not self.mongodb_manipulator.update_many_documents("organization", account, {"_id": project_id},
                                               {"connectiveStructureList": project_info["connectiveStructureList"],
                                                "connectiveStructureIdList": project_info["connectiveStructureIdList"],
                                                "connectiveStructureCount": project_id["connectiveStructureCount"]
                                                }):
                self.log.add_log("ExecutableStuffOrganizer: database error, cannot update to database", 3)
                return False, "database error"
            else:
                return True, "success"

        def modify_chain_list(operation, ids=None, info=None):

            """
            修改chain列表
            :param operation: 操作：添加/删除
            :param ids: 删除时填写
            :param info: 添加时填写
            :type info: list[dict, dict]
            :type ids: list
            :return: bool, str
            """
            self.log.add_log("ExecutableStuffOrganizer: modify_chain_list: %s connective structure" % operation, 1)

            project_info = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("organization", account, {"_id": project_id}, 1),
                ["projectId"]
            )[0]

            if operation == "add":
                if type(info) != list:
                    self.log.add_log("ExecutableStuffOrganizer: type error, in the operation-add, param-info must be a list and its elements must be dict", 3)
                    return False, "type error, operation-add requires param-info in type-list and its elements in type-dict"

                # add chain
                chain_info_template_raw = json.load(
                    open("./backend/data/json/project_chain_info_template.json", "r", encoding="utf-8"))
                for chain_info in info:
                    chain_info_template = chain_info_template_raw

                    # step.1 load basic params
                    chain_info_template["last"] = chain_info["last"]
                    chain_info_template["next"] = chain_info["next"]
                    chain_info_template["content"] = chain_info["content"]

                    # step.3 generate chain_id
                    project_info["chainCount"] += 1
                    chain_id = self.encryption.md5(project_info["chainCount"] + self.encryption.generate_random_key())
                    while chain_id in project_info["chainIdList"]:
                        chain_id = self.encryption.md5(project_info["chainCount"] + self.encryption.generate_random_key())
                    chain_info_template["chainId"] = chain_id

                    project_info["chainIdList"].append(chain_id)
                    project_info["chainList"][chain_id] = chain_info_template
            elif operation == "delete":
                if type(ids) != list:
                    self.log.add_log("ExecutableStuffOrganizer: type error, param-ids must be a list while operation-delete, exit", 3)
                    return False, "type error, param-ids must be a list"

                # delete cs
                chain_id_list = project_info["chainIdList"]
                for chain_id in ids:
                    # step.1 is chain_id exist
                    if chain_id not in chain_id_list:
                        self.log.add_log("ExecutableStuffOrganizer: chain-%s does not exist, skip" % chain_id, 3)
                        continue

                    # step.3 delete chain in normal
                    del project_info["chainList"][chain_id]
                    project_info["chainIdList"].remove(chain_id)
                    project_info["chainCount"] -= 1

            else:
                self.log.add_log("ExecutableStuffOrganizer: unknown operation-%s, exit" % operation, 3)
                return False, "unknown operation-%s" % operation

            # step.4 update to database
            if not self.mongodb_manipulator.update_many_documents("organization", account, {"_id": project_id},
                                                                  {"chainList": project_info["chainList"],
                                                                   "chainIdList": project_info["chainIdList"],
                                                                   "chainCount": project_id["chainCount"]
                                                                   }):
                self.log.add_log("ExecutableStuffOrganizer: database error, cannot update to database", 3)
                return False, "database error"
            else:
                return True, "success"

        # assign functions based on mode

        if mode == 1 or mode == "modify_stu_ref_list":
            try:
                mandatory_operation = param["mandatory_operation"]
            except KeyError:
                mandatory_operation = True
            return modify_stuff_reference_list(param["type"], param["operation"], param["ids"], mandatory_operation)
        else:
            optional_param = ["ids", "info"]
            ids, info = None, None
            for key in optional_param:
                try:
                    if key == "ids":
                        ids = param["ids"]
                    elif key == "info":
                        info = param["info"]
                except KeyError:
                    pass
            if mode == 2 or mode == "modify_chunk_list":
                return modify_chunk_list(param["operation"], ids=ids, info=info)
            elif mode == 3 or mode == "modify_cs_list":
                return modify_cs_list(param["operation"], ids=ids, info=info)
            elif mode == 4 or mode == "modify_chain_list":
                return modify_chain_list(param["operation"], ids=ids, info=info)
            else:
                self.log.add_log("ExecutableStuffOrganizer: mode-%s does not supported in modify_project_workflow, exit" % mode, 3)
                return False, "mode-%s does not supported"

    def edit_workflow_element(self, account, project_id, mode, param):

        """
        编辑workflow元素：即编辑组成workflow的元素：chunk/chain/cs的配置信息
        :param account: 账户名
        :param project_id: project id
        :param mode: 编辑内容：chunk/cs/chain
        :param param: 参数，其中的内容依据编辑内容而定
        :type param: dict
        :return: bool, str
        """
        self.log.add_log("ExecutableStuffOrganizer: edit_workflow_element: mode-%s start" % mode, 1)

        project_info = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document("organization", account, {"_id": project_id}, 1),
            ["projectId"]
        )[0]

        def modify_chunk_info():

            """
            修改chunk信息
            :return:
            """
            # 编辑「已有」块的信息
            all_chunk_ids = project_info["chunkIdList"]

            # step.1 load param
            try:
                chunk_id = param["chunk_id"]
            except KeyError:
                self.log.add_log("ExecutableStuffOrganizer: cannot find 'chunk_id' in param", 3)
                return False, "param-chunk_id lost"

            # step.2 is chunk_id exist
            if chunk_id not in all_chunk_ids:
                self.log.add_log("ExecutableStuffOrganizer: chunk-%s does not exist, exit" % chunk_id, 3)
                return False, "chunk-%s does not exist" % chunk_id

            # step.3 load changed keys
            changed_list = []
            for key in list(param.keys()):
                value = param[key]
                if key == "chunk_id":
                    continue
                elif key == "type":
                    if 0 <= int(value) <= 3:
                        project_info["chunkList"][chunk_id]["type"] = value
                        changed_list.append("type")
                    else:
                        self.log.add_log("ExecutableStuffOrganizer: chunk_type-%s does not supported" % value, 3)
                        return False, "chunk_type-%s does not supported" % value
                elif key == "content":
                    if "type" in changed_list:
                        changed_list.append(key)
                        project_info["chunkList"][chunk_id]["content"] = value
                    else:
                        self.log.add_log("ExecutableStuffOrganizer: to change 'content', you have to change type first",
                                         3)
                        return False, "you have to change 'type' first to change 'content'"
                elif key == "last" or key == "next":
                    # is id exist
                    if "chunk:" in value:
                        id_type = "chunkIdList"
                    elif "cs:" in value:
                        id_type = "connectiveStructureIdList"
                    else:
                        self.log.add_log("ExecutableStuffOrganizer: wrong value of 'last' or 'next', id_type error."
                                         "\n point: chunk-%s" % chunk_id, 3)
                        return False, "id_type is not found in 'last' or 'next'"

                    if value not in project_info[id_type]:
                        self.log.add_log("ExecutableStuffOrganizer: %s does not exist, can't add as '%s', exit"
                                         % (value, key), 3)
                        return False, "the value of '%s' does not correct or not exist" % key
                    else:
                        changed_list.append(key)
                        project_info["chunkList"][chunk_id][key] = value
                elif key == "relateTo":
                    project_info["relateTo"] = value
                    changed_list.append(key)

            # step.4 update to database
            if not self.mongodb_manipulator.update_many_documents("organization", account, {"_id": project_id},
                                                                  {"chunkList": project_info["chunkList"]}):
                self.log.add_log("ExecutableStuffOrganizer: database error, can't update data", 3)
                return False, "database error"
            else:
                return True, "success"

        if mode == "chunk":
            return modify_chunk_info()
        elif mode == "workflow":
            return modify_workflow_info()
        elif mode == "cs":
            return modify_cs_info()
        elif mode == "chain":
            return modify_chain_info()
        else:
            self.log.add_log("ExecutableStuffOrganizer: mode-%s does not supported" % mode, 3)
            return False, "mode-%s does not supported" % mode

    def generate_workflow(self, account, project_id, is_return=False):

        """
        计算出该project的工作流并存储
        :param account: 账户名
        :param project_id: project id
        :param is_return: 是否返回计算结果
        :type is_return: bool
        :return: bool, str
        """


