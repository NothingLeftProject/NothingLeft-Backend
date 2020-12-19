# coding=utf-8
# author: Lan_zhijiang
# description: backend init
# date: 2020/12/12

from backend.data.log import GtdLog
from backend.api.http.server import HttpServer
from backend.core.maintain.maintainer import Maintainer
from backend.api.http.http_handler import HttpHandler

import json
import threading


class BackendInit:

    def __init__(self):

        self.log = GtdLog()
        self.setting = json.load(open("./backend/data/json/setting.json", "r", encoding="utf-8"))

        self.Maintainer = Maintainer(self.log, self.setting)
        self.http_handler = HttpHandler(self.log, self.setting)
        self.http_server = HttpServer(self.log, self.setting, self.http_handler)

    def run_backend(self):

        """
        启动后端
        :return 
        """
        self.log.add_log("BackendInit: now start backend", 1)
        
        thread_server = threading.Thread(target=self.http_server.run_server, args=())
        thread_maintainer = threading.Thread(target=self.Maintainer.run, args=())
        thread_server.start()
        thread_maintainer.start()
