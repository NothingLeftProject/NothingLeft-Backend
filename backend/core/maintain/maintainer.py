# coding=utf-8
# author: Lan_zhijiang
# description: auto maintain the program
# date: 2020/12/13 (1937.12.13 勿忘国耻，铭记历史)


class Maintainer:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

    def run(self):

        """
        启动自动维护
        :return
        """
        self.log.add_log("Maintainer: start the auto maintain system", 1)
        self.log.add_log("Maintainer: maintainer still not finished", 1)
        
