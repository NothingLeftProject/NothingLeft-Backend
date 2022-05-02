# coding=utf-8
# author: Lan_zhijiang
# description: http server (build by flask) (遵守restfulAPI)
# date: 2022/5/2
# GET: Read; POST: Create; PUT: Update; PATCH: PartlyUpdate; DELETE: Delete
"""
遵守RestfulAPI设计，支持POST覆盖其它操作
    flask创建app

"""


from flask import *
import json

from backend.api.network.http.http_handler import HttpHandler
from backend.data.log import Log

flask_app = Flask(__name__)
base_abilities = None


def run_server(ba):

    """
    启动服务器
    :return:
    """
    setting = ba.setting["httpServer"]
    log = Log(ba.parent_log, "HttpServer")
    log.add_log("Start http server...", 1)

    global base_abilities
    base_abilities = ba

    log.add_log("http server listening on %s:%s" % (setting["bindIp"], str(setting["bindPort"])), 1)
    flask_app.run(host=setting["bindIp"], port=setting["httpPort"])


@flask_app.route('/<operate_class/<target_id>>', methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def handle_request(operate_class, target_id):

    """
    处理请求到/路径下的请求
    :return:
    """
    return HttpHandler(base_abilities).handle_request(request)


class HttpServer:

    def __init__(self, ba):

        self.ba = ba

    def run_server(self):

        """
        启动服务器
        :return
        """
        run_server(self.ba)
