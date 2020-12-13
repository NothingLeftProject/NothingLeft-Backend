# coding=utf-8
# author: Lan_zhijiang
# description: http command finder
# date: 2020/12/13 (1937.12.13 勿忘国耻，铭记历史)

from backend.api.local.local_caller import LocalCaller


class CommandFinder:

    def __init__(self, log, setting):

        self.local_caller = LocalCaller(log, setting)

        self.all_command_list = {
            "sign_up": self.local_caller.user_sign_up,
            "login": self.local_caller.user_login
        }
