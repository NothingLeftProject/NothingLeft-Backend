# coding=utf-8
# author: Lan_zhijiang
# description: http server (build by flask)
# date: 2020/12/12

from flask import Flask
from flask import request
from bakend.api.http.http_handler import HttpHandler
import json
import socket

setting = json.load(open("./backend/data/json/setting.json", encoding="utf-8"))
flask_app = Flask(__name__)
achhc = 0


def get_ip():

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def run_server(class_log, setting):

    """
    启动服务器
    :return:
    """
    class_log.add_log("HttpServer: Start http server...", 1)
    class_log.add_log("HttpServer: ServerAddr: " + setting["hostIp"] + str(setting["httpPort"]), 1)

    flask_app.run(host=get_ip(), port=setting["httpPort"])
    global achhc
    achhc = HttpHandler(class_log, setting)


@flask_app.route('/api', methods=['POST'])
def route_api():

    """
    处理请求到/api路径下的请求
    :return:
    """
    achhc.set_request_data(request.get_json(force=True))
    return json.dumps(achhc.handle_request())


class HttpServer:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

    def run_server(self):

        """
        启动服务器
        :return
        """
        run_server(self.log, self.setting)
