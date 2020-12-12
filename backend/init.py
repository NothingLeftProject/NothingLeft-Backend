# coding=utf-8
# author: Lan_zhijiang
# description: backend init
# date: 2020/12/12

from data.log import GtdLog
import api.http.server
from core.maintain.maintainer import Maintainer

import json
import threading


class BackendInit:

    def __init__(self):

        self.log = GtdLog()
        self.setting = json.load(open("./data/json/setting.json", "r", encoding="utf-8"))

        self.Maintainer = Maintainer(self.log, self.setting)

    def run_backend(self):

        """
        启动后端
        :return 
        """
        self.log.add_log("BackendInit: now start backend", 1)
        
        thread_server = threading.Thread(target=server.run_server, args=(self.log, self.setting,))
        thread_maintainer = threading.Thread(target=self.Maintainer.run, args=())
        thread_server.start()
        thread_maintainer.start()