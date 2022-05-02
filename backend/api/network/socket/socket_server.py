# coding=utf-8
# author: Lan_zhijiang
# description socket server(基于TCP/UDP的ScoketAPI服务端，Handler对象为服务端与客户端建立连接的处理对象)
# date: 2022/4/21
# configuration of setting.json["socketServer"]
#     bindIp, bindPort, maxQueueSize, connProtocol

import socket
import threading
import json
from universal.log import Log
from api.network.socket.socket_handler import SocketHandler

base_abilities = None


def run_server(ba):

    """
    启动Socket服务器
    :return:
    """
    log = Log(ba.parent_log, "SocketServer")
    setting = ba.setting["socketServer"]
    c_p = setting["connProtocol"]

    log.add_log("Start socket server...", 1)

    global base_abilities
    base_abilities = ba

    log.add_log("socket server listening on: %s" % setting["bindIp"] + ":%s" % setting["bindPort"], 1)

    if c_p == "UDP":
        c_p = socket.SOCK_DGRAM
    elif c_p == "TCP":
        c_p = socket.SOCK_STREAM

    websocket_server = socket.socket(socket.AF_INET, c_p)
    websocket_server.bind((setting["bindIp"], setting["bindPort"]))
    websocket_server.listen(setting["maxQueueSize"])
    log.add_log("server start, wait for client to connect...", 1)
    while True:
        conn, addr = websocket_server.accept()
        thread = threading.Thread(target=receive_new_conn, args=(conn, addr))
        thread.setDaemon(True)
        thread.start()


def receive_new_conn(conn, addr):
    SocketHandler(base_abilities, addr).handle_conn(conn)


class SocketServer:

    def __init__(self, ba):

        self.ba = ba

    def run_server(self):

        """
        启动服务器
        :return
        """
        run_server(self.ba)

