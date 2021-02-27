# coding=utf-8
# author: Lan_zhijiang
# description: http command finder
# date: 2020/12/13 (1937.12.13 勿忘国耻，铭记历史)

from backend.api.local.local_caller import LocalCaller


class CommandFinder:

    def __init__(self, log, setting, caller):

        self.local_caller = LocalCaller(log, setting, caller)

        self.all_command_list = {
            "user_sign_up": self.local_caller.user_sign_up,
            "user_login": self.local_caller.user_login,
            "user_logout": self.local_caller.user_logout,
            "user_delete": self.local_caller.user_delete,
            "user_info_update": self.local_caller.user_info_update,
            "user_info_get_all": self.local_caller.user_info_get_all,
            "user_info_get_one_multi": self.local_caller.user_info_get_one_multi,
            "user_info_get_multi_multi": self.local_caller.user_info_get_multi_multi,
            "user_get_permissions": self.local_caller.user_get_permissions,
            "user_write_permissions": self.local_caller.user_write_permissions,
            "user_edit_permissions": self.local_caller.user_edit_permissions,
            "user_group_add_users": self.local_caller.user_group_add_users,
            "user_group_remove_users": self.local_caller.user_group_remove_users,
            "user_group_move_one_to_one": self.local_caller.user_group_move_one_to_one,
            "user_group_add": self.local_caller.user_group_add,
            "user_group_remove": self.local_caller.user_group_remove,
            "user_group_get_permissions": self.local_caller.user_group_get_permissions,
            "stuff_add": self.local_caller.stuff_add
        }
