# coding=utf-8
# author: Lan_zhijiang
# description: auto maintain the program
# date: 2020/12/13 (1937.12.13 勿忘国耻，铭记历史)

from backend.user.user_manager import UserManager


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

        if "superuser" not in self.mongodb_manipulator.collection_names_list["user_group"]:
            self.user_group_manager.add_user_group("superuser")

        if "root" not in self.mongodb_manipulator.collection_names_list["user"]:
            root_key = self.encryption.generate_random_key()
            self.user_manager.sign_up("root", root_key,
                                      "root@root.com", "superuser")

            self.log.add_log("Maintainer: add superuser success, token: " + root_key)
