# coding=utf-8
# author: Lan_zhijiang
# description: socket handler: socket连接处理，一个SocketHandler处理一个客户端
# lastEditedDate: 2022/5/1

import time
import threading
from universal.log import Log
from database.mongodb import MongoDBManipulator


class SocketHandler:

    def __init__(self, ba, addr_object):

        self.ba = ba
        self.parent_log = ba.parent_log
        self.log = Log(self.parent_log, "SocketHandler")
        self.setting = ba.setting

        self.addr_object = addr_object

        self.mongodb_manipulator = MongoDBManipulator(self.ba, self.setting)

        self.socket_conn_list = {}
        self.lost_conn_list = {}

        self.socket_conn = None
        self.status = False
        self.client_account = ""
        self.client_type = ""

        self.last_heartbeat_time_stamp = 0

        self.res_handler = {}
        self.req_handler = {}

    def send(self, string):

        """
        发送
        """
        try:
            self.socket_conn.send(string.encode("utf-8"))
        except OSError:
            self.status = False
            self.log.add_log("connection with %s_client-%s has closed by accident" % (self.client_type, self.client_account), 3)
            try:
                client_status_list = list(self.mongodb_manipulator.get_document("interview", "calling", {"_id": "client_status"}, 1))[0][self.client_account]
                client_status_list[self.client_account] = False
                self.mongodb_manipulator.update_many_documents("interview", "calling", {"_id": "client_status"},
                                                               {self.client_account: client_status_list})
                del self.socket_conn_list[self.client_type][self.client_account]
            except KeyError:
                self.log.add_log("not connected?! can't find %s in conn_list" % self.client_account, 3)

    def recv(self, length):

        """
        接收
        """
        try:
            return self.socket_conn.recv(length).decode("utf-8")
        except OSError:
            self.log.add_log("connection with %s_client-%s has closed by accident" % (self.client_type, self.client_account), 3)
            try:
                client_status_list = list(self.mongodb_manipulator.get_document("interview", "calling", {"_id": "client_status"}, 1))[0][self.client_account]
                client_status_list[self.client_account] = False
                self.mongodb_manipulator.update_many_documents("interview", "calling", {"_id": "client_status"},
                                                               {self.client_account: client_status_list})
                self.status = False
                del self.socket_conn_list[self.client_type][self.client_account]
            except KeyError:
                self.log.add_log("not connected?! can't find %s in conn_list" % self.client_account, 3)

    def auth(self, account, user_type, token):

        """
        进行认证
        :param account: 賬戶
        :param user_type: 用戶類型
        :param token: token
        :return bool
        """
        if self.mongodb_manipulator.is_collection_exist(user_type, account) is False:
            self.log.add_log("account not exists or format error, auth fail", 1)
            return False, "account not exist"

        is_online = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document(user_type, account, {"isOnline": 1}, 2),
            ["isOnline"]
        )[0]["isOnline"]
        if not is_online:
            self.log.add_log("user-%s" % account + " haven't login yet", 1)
            return False, "user haven't login yet"

        # is token same
        real_token = self.mongodb_manipulator.parse_document_result(
            self.mongodb_manipulator.get_document(user_type, account, {"token": 1}, 2),
            ["token"]
        )[0]["token"]
        if real_token == token:
            # auth pass
            return True, "success"
        else:
            # auth fail, wrong token
            self.log.add_log("wrong token, auth fail", 1)
            return False, "wrong token"

    def parse_recv(self, recv):

        """
        解析接收的信息
        :param recv: 接收的信息
        :return:
        """
        if recv is None:
            self.log.add_log("error message, None Type", 3)
            return None, None, None
        try:
            a = recv.split("?")
            command, param_raw = a[0], a[1]
            b = command.split(":")
            command_type, command = b[0], b[1]
        except IndexError:
            return None, None, None
        param = {}
        param_raw = param_raw.split("&")
        try:
            for i in param_raw:
                i_split = i.split("=")
                param[i_split[0]] = i_split[1]
        except IndexError:
            pass
        return command, command_type, param

    def handle_conn(self, conn):

        """
        處理連接
        :param conn: socket连接
        :return
        """
        self.log.add_log("receive new websocket conn", 1)
        self.last_heartbeat_time_stamp = self.parent_log.get_time_stamp()
        self.socket_conn = conn
        recv = self.recv(1024)
        self.log.add_log("receive first command, start handle", 1)

        command, command_type, param = self.parse_recv(recv)
        if command == "auth":
            self.last_heartbeat_time_stamp = self.parent_log.get_time_stamp()
            try:
                account, token, user_type = param["account"], param["token"], param["userType"]
            except KeyError:
                self.log.add_log("param not complete, close", 3)
                return
            res, err = self.auth(account, user_type, token)
            if res:
                # auth success, join self into list, can start communicate
                self.log.add_log("auth success", 1)
                a = "res:auth?code=0&msg=%s" % err
                ws.send(a.encode("utf-8"))
                if account in self.lost_conn_list[user_type]:
                    self.lost_conn_list[user_type].remove(account)

                if user_type == "waiting_room":
                    if account == "5":
                        for i in range(1, 61):
                            self.socket_conn_list[user_type]["com%s" % str(i)] = self
                    elif account == "6":
                        for i in range(61, 112):
                            self.socket_conn_list[user_type]["com%s" % str(i)] = self
                self.socket_conn_list[user_type][account] = self

                self.client_account = account
                self.client_type = user_type
                self.status = True

                # update database
                client_status_list = list(self.mongodb_manipulator.get_document("interview", "calling", {"_id": "client_status"}, 1))[0]
                client_status_list = client_status_list[user_type]
                client_status_list[account] = "online"
                self.mongodb_manipulator.update_many_documents("interview", "calling", {"_id": "client_status"}, {user_type: client_status_list})

                self.log.add_log("%s_client-%s successfully establish connection with server " % (self.client_type, self.client_account), 1)
                self.send("auth?code=0&msg=success")

                auto_close_thread = threading.Thread(target=self.auto_close_conn, args=())
                auto_close_thread.start()
                self.communicate()
            else:
                # auth failed
                self.log.add_log("auth failed", 1)
                self.send("res:auth?code=1&msg=%s" % err)
        else:
            self.log.add_log("client don't send an auth, close", 2)
            self.send("You fucking fool, you should tell me who you are first!")

        return

    def communicate(self):

        """
        開始交流（維持連接）
        :return
        """
        self.log.add_log("start communicate with %s_client-%s" % (self.client_type, self.client_account), 1)
        while True:
            # wait command
            recv = self.recv(1024)
            # parse command
            self.log.add_log("receive message from client-%s, start handle" % self.client_account, 0)
            command, command_type, param = self.parse_recv(recv)
            self.last_heartbeat_time_stamp = self.parent_log.get_time_stamp()
            if command is None or command_type is None:
                self.send("res:res?code=1&msg=wrong format of message")
            else:
                if command_type == "req":
                    self.recv_command(command, param)
                elif command_type == "res":
                    self.recv_response(command, param)
                else:
                    self.send("res:%s?code=1&msg=wrong format of message" % command)

    def recv_command(self, command, param):

        """
        处理接受到的指令
        :param command: 指令
        :param param: 参数
        """
        if command == "heartbeat":
            self.log.add_log("client-%s heartbeat success" % self.client_account, 0)
            self.send("res:heartbeat?code=0&msg=done")
            return

        self.log.add_log("recv_command-%s from client-%s" % (command, self.client_account), 1)
        self.req_handler[command](param, self)

    def recv_response(self, command, response):

        """
        处理响应
        :param command: 响应的指令
        :param response: 返回
        """
        self.log.add_log("recv_response-%s from client-%s" % (command, self.client_account), 1)
        try:
            self.res_handler[command](response)
        except KeyError:
            # normal handle
            self.common_recv_response(response)

    def common_recv_response(self, response):

        """
        通用响应处理
        :param response: 响应
        """
        self.log.add_log("common_recv_response is now process response", 1)
        if response["code"] != "0":
            self.log.add_log("command execute not success, response is %s" % response["code"], 3)
        return

    def send_command(self, command, param, res_func=None):

        """
        发送指令
        :param command: 命令
        :param param: 参数
        :param res_func: 接受响应的函数
        :return
        """
        self.log.add_log("send_command-%s to client-%s" % (command, self.client_account), 1)
        if res_func is None:
            res_func = self.common_recv_response
        param_str = ""
        for i in list(param.keys()):
            param_str = param_str + "%s=%s" % (i, param[i]) + "&"
        param_str = param_str[0:-1]

        send_str = "req:%s?%s" % (command, param_str)
        self.send(send_str)
        self.res_handler[command] = res_func

    def send_response(self, command, param):

        """
        发送响应
        :param command: 响应的指令
        :param param: 参数
        :return
        """
        self.log.add_log("send_response to client-%s" % self.client_account, 1)
        param_str = ""
        for i in list(param.keys()):
            param_str = param_str + "%s=%s" % (i, param[i]) + "&"
        param_str = param_str[0:-1]

        send_str = "res:%s?%s" % (command, param_str)
        self.send(send_str)

    def auto_close_conn(self):

        """
        检验心跳时间，超时则断开
        :return
        """
        self.log.add_log("start auto_close_conn", 1)
        while True:
            now_time_stamp = self.parent_log.get_time_stamp()
            time_loss = int(now_time_stamp) - int(self.last_heartbeat_time_stamp)
            if time_loss > 10:
                self.log.add_log("auto_close_conn: heartbeat has stopped for too long, close connection", 2)
                self.socket_conn.close()
                self.status = "inactive"
                break
            time.sleep(30)

        try:
            self.lost_conn_list[self.client_type].append(self.client_account)
            del self.socket_conn_list[self.client_type][self.client_account]
        except KeyError:
            self.log.add_log("client-%s has already down and closed socket connection" % self.client_account, 1)

