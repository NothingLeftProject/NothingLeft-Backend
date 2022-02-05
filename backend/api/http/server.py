# coding=utf-8
# author: Lan_zhijiang
# description: http server (build by flask)
# date: 2020/12/12

from flask import Flask, request
from backend.api.http.http_handler import HttpHandler
import json
import socket

flask_app = Flask(__name__)
log_class = {}
settings = {}


def get_ip():

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def run_server(b_a):

    """
    启动服务器
    :return:
    """
    setting = b_a.setting
    b_a.log.add_log("HttpServer: Start http server...", 1)

    try:
        if type(setting["bindIp"]) is not str or setting["bindIp"] == "":
            raise KeyError
    except KeyError:
        setting["bindIp"] = str(get_ip())
        json.dump(setting, open("./backend/data/json/setting.json", "w", encoding="utf-8"))

    global base_abilities
    base_abilities = b_a

    b_a.log.add_log("HttpServer: ServerAddr: " + setting["bindIp"] + ":" +  str(setting["httpPort"]), 1)
    flask_app.run(host=setting["bindIp"], port=setting["httpPort"])


@flask_app.route('/api', methods=["POST", "GET"])
def route_api():

    """
    处理请求到/api路径下的请求
    :return:
    """
    return json.dumps(HttpHandler(base_abilities).handle_request(request.get_json(force=True)))


class HttpServer:

    def __init__(self, base_abilities):

        self.base_abilities = base_abilities

    def run_server(self):

        """
        启动服务器
        :return
        """
        run_server(self.base_abilities)
