# coding=utf-8
# author: Lan_zhijiang
# description: http handler
# date: 2022/5/2

import json

from backend.api.network.http.urls import Urls
from backend.database.mongodb import MongoDBManipulator
from backend.data.log import Log


class HttpHandler:

    def __init__(self, ba):

        self.ba = ba
        self.parent_log = ba.parent_log
        self.log = Log(self.parent_log, "HttpHandler")
        self.setting = ba.setting

        self.request = None
        self.request_headers = None
        self.request_data = None
        self.request_method = None
        self.request_path = None

        self.response_body = None
        self.response_headers = None
        self.response_code = 200

        self.permission_list = None

        self.response_body_raw = json.load(open("./backend/data/json/http_template/response_body_template.json", "r", encoding="utf-8"))
        self.response_headers_raw = json.load(open("./backend/data/json/http_template/response_headers_templates.json", "r", encoding="utf-8"))

        self.special_auth_pass = False
        self.special_auth_pass_type = None

        self.mongodb_client = self.ba.mongodb_client
        self.mongodb_manipulator = MongoDBManipulator(self.ba, self.mongodb_client)
        self.urls = None

    def auth(self):

        """
        进行认证
        :return bool
        """
        self.log.add_log("start auth", 1)

        user = self.request_headers["user"]
        user_type = self.request_headers["userType"]
        # is user_type correct
        if user is not None and user != "":
            user_type = self.request_data["header"]["userType"]
            if user_type not in ["user"]:
                self.log.add_log("user_type not correct, auth fail", 1)
                self.response_body["msg"] = "user_type error"
                return False

        now_time_stamp = self.parent_log.get_time_stamp()
        try:
            gave_time_stamp = self.response_headers["timeStamp"]
        except KeyError:
            self.log.add_log("headers is not complete", 1)
            self.response_body["msg"] = "headers is not complete"
            return False

        time_loss = abs(int(now_time_stamp) - int(gave_time_stamp))  # might not be safe here

        # is time stamp in law
        if 0 <= time_loss <= 600:
            if user is None or user == "":
                self.log.add_log("user is none, auth failed", 3)
                return False
            last_login_time_stamp = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document(user_type, user, {"lastLoginTimeStamp": 1}, 2),
                ["lastLoginTimeStamp"]
            )[0]["lastLoginTimeStamp"]

            try:
                login_time_loss = abs(int(gave_time_stamp) - int(last_login_time_stamp))
            except TypeError:
                self.log.add_log("user-%s haven't login for once yet" % user, 1)
                self.response_body["msg"] = "user-%s haven't login for once yet" % user
                return False
            else:
                self.log.add_log("user-%s's LLTS: %s" % (user, last_login_time_stamp), 1)
                is_online = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document(user_type, user, {"isOnline": 1}, 2),
                    ["isOnline"]
                )[0]["isOnline"]
                if not is_online:
                    self.log.add_log("user-%s haven't login yet" % user, 1)
                    self.response_body["msg"] = "user-%s haven't login yet" % user
                    return False

            # is token valid
            if 0 <= login_time_loss <= 3600 * self.setting["user"]["loginValidTime"]:
                self.log.add_log("time stamp is in law", 1)

                # is token same
                real_token = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document(user_type, user, {"token": 1}, 2),
                    ["token"]
                )[0]["token"]
                need_verify_token = self.request_headers["token"]
                if real_token == need_verify_token:
                    # auth pass
                    self.mongodb_manipulator.update_many_documents("user", user, {"_id": 13}, {"lastLoginTimeStamp": self.parent_log.get_time_stamp()})
                    return True
                else:
                    # auth fail, wrong token
                    self.log.add_log("wrong token, auth fail", 1)
                    self.response_body["msg"] = "wrong token"
                    return False
            else:
                # auth fail, login outdated
                self.log.add_log("login outdated, auth fail", 1)
                self.response_body["msg"] = "login outdated, please login"  # login outdated error
                return False
        else:
            # auth fail, time stamp not in law
            self.log.add_log("time stamp not in law, time_loss > 600, auth fail", 1)
            self.response_body["msg"] = "time_loss > 600, check your network or timezone"  # timestamp error
            return False

    def handle_request(self, request):

        """
        处理请求
        :param request: 请求
        :return bool
        """
        # ATTENTION: 防压测任务！
        self.log.add_log("received http request, start handle...", 1)

        self.response_body = self.response_body_raw.copy()
        self.response_body["responses"] = {}
        self.response_headers = self.response_headers_raw.copy()
        self.request = request
        self.request_data = request.get_json(force=True)
        self.request_headers = request.headers
        self.request_method = request.method
        self.request_path = request.url.replace("/api/", "")

        # 绕过auth的唯二方式：login和signup
        if self.request_method == "GET" and "/user/login" in self.request_path:
            # login request
            self.log.add_log("a login request, specially allow", 1)
            self.special_auth_pass = True
            self.special_auth_pass_type = "login"
        elif self.request_method == "POST" and "/user/signup" in self.request_path:
            self.log.add_log("a signup request, specially allow", 1)
            if self.setting["user"]["allowSignup"]:
                self.special_auth_pass = True
                self.special_auth_pass_type = "signup"
            else:
                self.response_body["msg"] = "signup was not allowed by user, please contact your admin"
                self.log.add_log("self-signup was not allowed", 1)

        if self.auth() or self.special_auth_pass:
            user = self.request_headers["user"]
            user_type = self.request_headers["userType"]
            self.urls = Urls(self.ba, user, user_type)

            try:
                path_split = self.request_path.split("/")
                command_target = path_split[-1]
                command_name = self.request_path.replace(command_target)
                command_param = self.request_data["param"]
            except KeyError:
                self.log.add_log("the command info is wrong, 'param' lost", 1)
                self.response_body["msg"] = "command_info wrong, 'param' lost"
                self.response_code = 400
                command_name = None
            else:
                self.response_body["commandName"] = command_name
                self.permission_list = self.mongodb_manipulator.parse_document_result(
                    self.mongodb_manipulator.get_document(user_type, user, {"permissionList": 1}, 2),
                    ["permissionList"]
                )[0]["permissionList"]

                if command_name in self.permission_list or self.special_auth_pass:
                    self.log.add_log("command-%s is allowed, start handle" % command_name, 1)
                    try:
                        command_handle_function = self.urls.command_list[self.request_method][command_name]
                    except KeyError:
                        self.log.add_log("can't find command-%s in urls-method-%s, skip" % (command_name, self.request_method), 3)
                        self.response_body["msg"] = "can't find command in urls, check your commandName(path) and httpMethod"
                        self.response_code = 404
                    else:
                        # real handle
                        res, err, http_code = command_handle_function(command_target, command_param)
                        self.response_code = http_code  # http_code就是code
                        self.response_body["msg"] = err
                        self.response_body["result"] = res
                else:
                    self.response_body["msg"] = "you have no permission requesting command-%s or wrong command name" % command_name
                    self.response_body["result"] = None
                    self.response_code = 403

            self.log.add_log("command-%s handle completed" % command_name, 1)
        else:
            self.log.add_log("auth fail", 1)
            self.response_body["msg"] = "auth fail"
            self.response_code = 401

        self.response_headers["timeStamp"] = self.parent_log.get_time_stamp()
        return self.response_body, self.response_code, self.response_headers
