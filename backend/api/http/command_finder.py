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
            "stuff_add": self.local_caller.stuff_add,
            "stuff_modify": self.local_caller.stuff_modify,
            "stuff_get_many": self.local_caller.stuff_get_many,
            "stuff_get_id_from_condition": self.local_caller.stuff_get_id_from_condition,
            "stuff_get_id_from_preset": self.local_caller.stuff_get_id_from_preset,
            "stuff_delete_many": self.local_caller.stuff_delete_many,
            "stuff_generate_preset_list": self.local_caller.stuff_generate_preset_list,
            "stuff_set_many_status": self.local_caller.stuff_set_many_status,
            "stuff_set_many_level": self.local_caller.stuff_set_many_level,
            "stuff_is_exist": self.local_caller.stuff_is_exist,
            "stuff_add_many_custom_attribute": self.local_caller.stuff_add_many_custom_attribute,
            "stuff_add_events": self.local_caller.stuff_add_events,
            "stuff_remove_events": self.local_caller.stuff_remove_events,
            "stuff_set_event_status": self.local_caller.stuff_set_event_status
        }
