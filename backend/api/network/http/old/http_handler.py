# coding=utf-8
# author: Lan_zhijiang
# description: http handler
# date: 2020/12/12

import json

from backend.user.user_permission_mamanger import UserPermissionManager
from backend.api.network.http.old.command_finder import CommandFinder


class HttpHandler:

    def __init__(self, base_abilities):

        self.base_abilities = base_abilities
        self.log = base_abilities.log
        self.setting = base_abilities.setting

        self.request_data = {}
        self.permission_list = []
        self.response_data_raw = json.load(open("./backend/data/json/response_body_template.json", "r", encoding="utf-8"))
        self.response_data = {}
        self.special_auth_pass = False
        self.special_auth_pass_type = ""

        # self.mongodb_manipulator = MongoDBManipulator(log, setting)
        self.mongodb_manipulator = self.base_abilities.mongodb_manipulator
        self.permission_manager = UserPermissionManager(self.base_abilities)
        self.command_finder = ""

    def auth(self):

        """
        进行认证
        ATTENTION: the development of "root"
        :return bool
        """
        self.log.add_log("HttpHandler: start auth", 1)

        # is the user exists
        account = self.request_data["header"]["account"]
        if "@" in account or str(account) == account:  # ATTENTION: error might be here
            now_time_stamp = self.log.get_time_stamp()
            try:
                gave_time_stamp = self.request_data["header"]["timeStamp"]
            except KeyError:
                self.log.add_log("HttpHandler: param is not complete", 1)
                self.response_data["header"]["errorMsg"] = "param is not complete"
                return False

            time_loss = abs(int(now_time_stamp) - int(gave_time_stamp)) # might not safe here

            # is time stamp in law
            if 0 <= time_loss <= 600:

                param = ["loginRequest", "signupRequest"]
                for key in param:
                    try:
                        if key == "loginRequest":
                            if self.request_data["header"]["loginRequest"]:
                                self.special_auth_pass = True
                                self.special_auth_pass_type = "login"
                                return True
                        elif key == "signupRequest":
                            if self.request_data["header"]["signupRequest"]:
                                self.special_auth_pass = True
                                self.special_auth_pass_type = "signup"
                                return True
                    except KeyError:
                        pass

                last_login_time_stamp = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document("user", account, {"lastLoginTimeStamp": 1}, 2),
                    ["lastLoginTimeStamp"]
                )[0]["lastLoginTimeStamp"]

                try:
                    login_time_loss = abs(int(gave_time_stamp) - int(last_login_time_stamp))
                except TypeError:
                    self.log.add_log("HttpHandler: user-" + account + " haven't login for once yet", 1)
                    self.response_data["header"]["errorMsg"] = "user-" + account + " haven't login for once yet"
                    return False
                else:
                    self.log.add_log("HttpHandler: user-" + account + "'s LLTS: " + last_login_time_stamp, 1)
                    is_online = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("user", account, {"isOnline": 1}, 2),
                        ["isOnline"]
                    )[0]["isOnline"]
                    if not is_online:
                        self.log.add_log("HttpHandler: user-" + account + " haven't login yet", 1)
                        self.response_data["header"]["errorMsg"] = "user haven't login yet"
                        return False

                if 0 <= login_time_loss <= 3600 * self.setting["loginValidTime"]:
                    self.log.add_log("HttpHandler: time stamp is in law", 1)

                    # is token same
                    real_token = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("user", account, {"token": 1}, 2),
                        ["token"]
                    )[0]["token"]
                    need_verify_token = self.request_data["header"]["token"]
                    if real_token == need_verify_token:
                        # auth pass, load permission list
                        self.log.add_log("HttpHandler: token compared. load permissions list", 1)

                        self.permission_list, _ = self.permission_manager.get_user_permissions(account, ask_update=True)
                        if self.permission_list is False:
                            self.log.add_log("HttpHandler: can't load permission list", 3)
                            self.response_data["header"]["errorMsg"] = "database or something wrong with the backend"  # inside error
                            return False
                        try:
                            if self.request_data["header"]["isUpdateLLTS"]:
                                last_login_time_stamp = self.log.get_time_stamp()
                                self.setting["loginUsers"][account]["lastLoginTimeStamp"] = last_login_time_stamp
                                self.mongodb_manipulator.update_many_documents("user", account, {"_id": 13}, {"lastLoginTimeStamp": last_login_time_stamp})
                        except KeyError:
                            pass

                        return True
                    else:
                        # auth fail, wrong token
                        self.log.add_log("HttpHandler: wrong token, auth fail", 1)
                        self.response_data["header"]["errorMsg"] = "wrong token"
                        return False
                else:
                    # auth fail, login outdated
                    self.log.add_log("HttpHandler: login outdated, auth fail", 1)
                    self.response_data["header"]["errorMsg"] = "login outdated, please login"  # login outdated error
                    return False
            else:
                # auth fail, time stamp not in law
                self.log.add_log("HttpHandler: time stamp not in law, time_loss > 600, auth fail", 1)
                self.response_data["header"]["errorMsg"] = "time stamp is not in law, time_loss > 600"  # timestamp error
                return False
        else:
            # auth fail, param wrong
            self.log.add_log("HttpHandler: account not exists or format error, auth fail", 1)
            self.response_data["header"]["errorMsg"] = "user does not exists or format error"  # user not exists error
            return False

    def handle_request(self, request_data):

        """
        处理请求
        :param request_data: 请求数据
        :return bool
        """
        # ATTENTION: 防压测任务！
        self.log.add_log("HttpHandler: recevied http request, start handle...", 1)
        self.response_data = self.response_data_raw
        self.request_data = request_data

        if self.auth():
            self.command_finder = CommandFinder(self.base_abilities, self.request_data["header"]["account"])

            self.log.add_log("HttpHandler: auth completed", 1)
            special_handle_pass = False
            allow_process_command = True

            if self.special_auth_pass:
                if self.special_auth_pass_type == "login":
                    # the handle of login request
                    if self.request_data["header"]["loginRequest"]:
                        try:
                            command_name = self.request_data["command"][0]["commandName"]
                        except IndexError:
                            self.response_data["header"]["status"] = 1
                            self.response_data["header"]["errorMsg"] = "you lied to me! you are not here to login!"
                            allow_process_command = False
                            self.log.add_log("HttpHandler: can't find commandName", 1)
                        else:
                            if command_name != "user_login":
                                self.response_data["header"]["status"] = 1
                                self.response_data["header"]["errorMsg"] = "you lied to me! you are not here to login!"
                                allow_process_command = False
                                self.log.add_log("HttpHandler: false request to login", 1)
                            else:
                                self.response_data["header"]["status"] = 0
                                self.response_data["header"]["errorMsg"] = None
                                special_handle_pass = True
                elif self.special_auth_pass_type == "signup":
                    # the handle of signup request
                    if self.request_data["header"]["signupRequest"]:
                        if self.setting["allowSignup"]:
                            try:
                                command_name = self.request_data["command"][0]["commandName"]
                            except IndexError:
                                self.response_data["header"]["status"] = 1
                                self.response_data["header"]["errorMsg"] = "you lied to me! you are not here to sign up!"
                                allow_process_command = False
                                self.log.add_log("HttpHandler: can't find commandName", 1)
                            else:
                                if command_name != "user_sign_up":
                                    self.response_data["header"]["status"] = 1
                                    self.response_data["header"]["errorMsg"] = "you lied to me! you are not here to sign up!"
                                    allow_process_command = False
                                    self.log.add_log("HttpHandler: false request to sign up", 1)
                                else:
                                    self.response_data["header"]["status"] = 0
                                    self.response_data["header"]["errorMsg"] = None
                                    special_handle_pass = True
                        else:
                            self.response_data["header"]["status"] = 1
                            self.response_data["header"]["errorMsg"] = "not allow sign up free, please contact your admin"
                            allow_process_command = False
                            self.log.add_log("HttpHandler: not allow sign up free", 1)

            # the handle of normal command
            if allow_process_command:
                try:
                    request_commands = self.request_data["command"]
                except KeyError:
                    self.log.add_log("HttpHandler: can't find 'command' in the request")
                    self.response_data["header"]["errorMsg"] = "can't find command in your request"
                    self.response_data["header"]["status"] = 1
                else:
                    for command in request_commands:
                        command_response = {}
                        try:
                            command_name = command["commandName"]
                            command_param = command["param"]
                        except KeyError:
                            self.log.add_log("HttpHandler: the command info is wrong, 'commandName' or 'param' lost", 1)
                            command_response["status"] = 3
                            command_response["errorMsg"] = "command info wrong, 'commandName' or 'param' lost"
                            self.response_data["response"].append(command_response)
                            continue

                        command_response["commandName"] = command_name

                        if command_name in self.permission_list or special_handle_pass is True:
                            self.log.add_log("HttpHandler: " + command_name + " is allowed, start handle", 1)
                            try:
                                command_handle_function = self.command_finder.all_command_list[command_name]
                            except KeyError:
                                self.log.add_log(
                                    "HttpHandler: can't find command: " + command_name + " in command finder, skip", 3)
                                command_response["status"] = 1
                                command_response["errorMsg"] = "can't find command in command_finder"
                                self.response_data["response"].append(command_response)
                                continue
                            else:
                                function_response, err = command_handle_function(command_param)
                                if function_response is False:
                                    command_response["status"] = 1
                                    command_response["errorMsg"] = err
                                else:
                                    if err != "success":
                                        command_response["status"] = 2
                                    else:
                                        command_response["status"] = 0
                                    command_response["errorMsg"] = err
                                    command_response["result"] = function_response
                        else:
                            print(self.permission_list)
                            command_response["status"] = 2
                            command_response["errorMsg"] = "you have no permission to request command-" + command_name + " or wrong command name"
                            command_response["result"] = None
                        self.response_data["response"].append(command_response)
                        self.log.add_log("HttpHandler: command-%s handle completed" % command_name, 1)
                        special_handle_pass = False
        else:
            self.log.add_log("HttpHandler: auth fail", 1)
            self.response_data["header"]["status"] = 1

        self.response_data["header"]["timeStamp"] = self.log.get_time_stamp()

        return self.response_data
