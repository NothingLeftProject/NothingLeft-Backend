# coding=utf-8
# author: Lan_zhijiang
# description: http urls command finder
# date: 2022/4/9

from backend.api.local.local_caller import LocalCaller


class Urls:

    def __init__(self, ba, user, user_type):

        self.local_caller = LocalCaller(ba, user, user_type)

        self.command_list = {
            "GET": {
                "/user/login/": self.local_caller.user_login,
                "/user/logout/": self.local_caller.user_logout,
                "/user_info/all/": self.local_caller.user_info_get_all,
                "/user_info/multi/": self.local_caller.user_info_get_one_multi,
                "/stuff/": self.local_caller.stuff_get_many,
                "/stuff_id/": self.local_caller.stuff_get_id
            },
            "POST": {
                "/user/": self.local_caller.user_sign_up,
                "/user_group/": self.local_caller.user_group_add,
                "/stuff/": self.local_caller.stuff_add
            },
            "PUT": {
            },
            "PATCH": {
                "/user_info/": self.local_caller.user_info_update,  # include permission/belongedUserGroup...
                "/user_group/": self.local_caller.user_group_info_update,   # include permission/users... update
                "/stuff/": self.local_caller.stuff_modify
            },
            "DELETE": {
                "/user/": self.local_caller.user_delete,
                "/user_group/": self.local_caller.user_group_remove,
                "/stuff/": self.local_caller.stuff_delete_many
            }
        }
