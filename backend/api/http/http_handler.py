# coding=utf-8
# author: Lan_zhijiang
# description: http handler
# date: 2020/12/12

import json

from backend.database.mongodb import MongoDBManipulator
from backend.user.user_permission_mamanger import UserPermissionManager
from backend.api.http.command_finder import CommandFinder


class HttpHandler:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.mongodb_mainpulator = MongoDBManipulator(log, setting)
        self.permission_manager = UserPermissionManager(log, setting)
        self.command_finder = CommandFinder(log, setting)
        
        self.request_data = {}
        self.permission_list = []
        self.response_data = json.load(open("./backend/data/json/response_template.json", "r", encoding="utf-8"))

    def auth(self):

        """
        进行认证
        :return bool
        """
        self.log.add_log("HttpHandler: start auth", 1)
        # is the user exists
        account = self.request_data["header"]["account"]
        try:
            if "@" in account or str(int(account)) == account:  # ATTENTION: error might be here
                now_time_stamp = self.log.get_time_stamp()
                gave_time_stamp = self.request_data["header"]["timeStamp"]
                time_loss = int(now_time_stamp) - int(gave_time_stamp)

                # is time stamp in law
                if time_loss > 0 and time_loss < 60:
                    last_login_time_stamp = \
                    self.mongodb_mainpulator.get_document("user", account, query={"_id": 13}, mode=2)[
                        "lastLoginTimeStamp"]
                    login_time_loss = gave_time_stamp - last_login_time_stamp
                    if login_time_loss > 0 and login_time_loss < 3600 * 24:
                        self.log.add_log("HttpHandler: time stamp is in law", 1)

                        # is token same
                        real_token = self.mongodb_mainpulator.get_document("user", account, query={"_id": 7}, mode=2)[
                            "token"]
                        need_verify_token = self.response_data["header"]["token"]
                        if real_token == need_verify_token:
                            # auth pass, load permission list
                            self.permission_list = self.permission_manager.get_user_permissions(account)
                            if self.permission_list is False:
                                self.log.add_log("HttpHandler: can't load permission list", 3)
                                self.response_data["header"][
                                    "errorMsg"] = "database or something wrong with the backend"  # inside error
                                return False
                            return True
                    else:
                        self.log.add_log("HttpHandler: login outdate", 1)
                        self.response_data["header"]["errorMsg"] = "login outdate, please login"  # login outdate error
                else:
                    self.log.add_log("HttpHandler: time stamp not in law", 1)
                    self.response_data["header"]["errorMsg"] = "time stamp is not in law"  # timestamp error
                    return False
            else:
                self.log.add_log("HttpHandler: account not exists or format error", 1)
                self.response_data["header"]["errorMsg"] = "user does not exists or format error"  # user not exists error
                return False
        except ValueError:
            self.log.add_log("HttpHandler: account not exists or format error", 1)
            self.response_data["header"]["errorMsg"] = "user does not exists or format error"  # user not exists error
            return False

    def handle_request(self, request_data):

        """
        处理请求
        :param request_data: 请求数据
        :return bool
        """
        self.log.add_log("HttpHandler: recevied http request, start handle...", 1)
        self.request_data = request_data

        self.response_data["header"]["timeStamp"] = self.log.get_time_stamp()

        if self.auth():
            self.log.add_log("HttpHandler: auth completed", 1)

            request_commands = self.request_data["command"]
            for command in request_commands:
                try:
                    command_name = command["commandName"]
                    command_param = command["param"]
                except KeyError:
                    self.log.add_log("HttpHandler: the command info is wrong", 1)
                    command_response["status"] = 3
                    command_response["errorMsg"] = "command info wrong"
                    self.response_data["response"].append(command_response)
                    break
                
                command_response = {"commandName": command_name}

                if command_name in self.permission_list:
                    self.log.add_log("HttpHandler: " + command_name + " is allowed, start handle", 1)
                    try:
                        command_handle_function = self.command_finder.all_command_list[command_name]
                    except KeyError:
                        self.log.add_log("HttpHandler: can't find command: " + command_name + " in command finder, skip", 3)
                        command_response["status"] = 1
                        command_response["errorMsg"] = "can't find command in command_finder"
                        self.response_data["response"].append(command_response)
                        break
                    else:
                        function_response, err = command_handle_function(command_param)
                        if function_response is False:
                            command_response["status"] = 1
                            command_response["errorMsg"] = err
                        else:
                            command_response["status"] = 0
                            command_response["errorMsg"] = None
                            command_response["result"] = function_response
                        self.response_data["response"].append(command_response)
                    
        else:
            self.log.add_log("HttpHandler: auth fail", 1)
            self.response_data["header"]["status"] = 1

        return self.response_data
