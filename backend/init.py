# coding=utf-8
# author: Lan_zhijiang
# description: backend init
# date: 2020/12/12

from backend.database.mongodb import MongoDBManipulator
from backend.database.memcached import MemcachedManipulator
from backend.data.encryption import Encryption
from backend.data.log import GtdLog

from backend.api.http.server import HttpServer
from backend.core.maintain.maintainer import Maintainer

import json
import threading


class BaseAbilities:
    '''基础能力：log，MongoDB、MemcachedDB传递'''
    def __init__(self):

        self.log = GtdLog()
        self.setting = json.load(open("./backend/data/json/setting.json", "r", encoding="utf-8"))

        self.mongodb_manipulator = MongoDBManipulator(self.log, self.setting)
        self.memcached_manipulator = MemcachedManipulator(self.log, self.setting)
        self.encryption = Encryption()

class BackendInit:

    def __init__(self):

        self.base_abilities = BaseAbilities()
        
        self.Maintainer = Maintainer(self.base_abilities)
        self.http_server = HttpServer(self.base_abilities)

    def run_backend(self):

        """
        启动后端
        :return 
        """
        self.base_abilities.log.add_log("######## NL-BACKEND RUN NOW ########", 1)
        self.base_abilities.log.add_log("BackendInit: now start backend", 1)
        
        thread_server = threading.Thread(target=self.http_server.run_server, args=())
        thread_maintainer = threading.Thread(target=self.Maintainer.run, args=())
        thread_server.start()
        thread_maintainer.start()
