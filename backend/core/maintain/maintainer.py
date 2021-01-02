# coding=utf-8
# author: Lan_zhijiang
# description: auto maintain the program
# date: 2020/12/13 (1937.12.13 勿忘国耻，铭记历史)

from backend.user.user_manager import UserManager
import json


class Maintainer:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.user_manager = UserManager(self.log, self.setting)
        self.user_group_manager = self.user_manager.user_group_manager
        self.mongodb_manipulator = self.user_manager.mongodb_manipulator
        self.encryption = self.user_manager.encryption

    def run(self):

        """
        启动自动维护
        :return
        """
        self.log.add_log("Maintainer: start the auto maintain system", 1)

        self.log.add_log("Maintainer: checking database...", 1)
        self.mongodb_manipulator.get_database_names_list()

        database_check_list = [
            "user", "user_group"
        ]
        for event in database_check_list:
            if event not in self.mongodb_manipulator.database_names_list:
                self.mongodb_manipulator.add_database(event)
            else:
                self.log.add_log("Maintainer: database-" + event + " exists", 1)
            self.mongodb_manipulator.get_collection_names_list(event)

        if self.mongodb_manipulator.is_collection_exist("user_group", "superuser") is False:
            self.user_group_manager.add_user_group("superuser")

        if self.mongodb_manipulator.is_collection_exist("user", "root") is False:
            root_key = self.encryption.generate_random_key() + self.encryption.generate_random_key()
            root_key = self.encryption.md5(root_key)
            self.user_manager.sign_up("root", root_key,
                                      "root@root.com", "superuser")

            self.log.add_log("Maintainer: Your root account key: " + root_key, 1)

            root_permissions = json.load(open("./backend/data/json/root_permissions_list.json", "r", encoding="utf-8"))
            self.mongodb_manipulator.update_many_documents("user", "root", {"_id": 12}, {"permissionsList": root_permissions})

            self.log.add_log("Maintainer: add root success", 1)


