# coding=utf-8
# author: Lan_zhijiang
# desciption: inbox相关内容操作
# date: 2020/10/17

import json
import os


class GtdInboxManager():

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting
        self.inbox_path = self.setting["dataPath"] + "inbox/"

        self.inbox = {}
        self.get_inbox()

    def get_inbox(self):

        """
        获取inbox
        :return:
        """
        inbox_list = os.listdir(self.inbox_path)

        if inbox_list is None or inbox_list == []:
            info = {
                "numberOfStuff": 0
            }
            json.dump(info, open(self.inbox_path + "info.json", "w", encoding="utf-8"))

        for event in inbox_list:
            if event == "info.json":
                self.inbox["info"] = json.load(open(self.inbox_path+event, "r", encoding="utf-8"))
            else:
                self.inbox["stuff"].append(event.replace(".json", ""))  # 小于最大值不就得了？
                self.inbox["searchInfo"].append(
                    {"fileName": event, ""}
                )

    def update_inbox_to_local(self, stuff_info, stuff_path):

        """
        更新inbox到本地
        :param stuff_path: stuff路径
        :param stuff_info: stuff信息
        :return:
        """
        if stuff_info is not None and stuff_path is not None:  # may be a bug
            json.dump(stuff_info, open(stuff_path, "w", encoding="utf-8"))
        json.dump(self.inbox["info"], open(self.inbox_path + "info.json", "w", encoding="utf-8"))

    def add_stuff(self, name, tags=None, remarks=None, desc=None):

        """
        添加一个stuff到inbox中
        :param name: stuff的名称
        :param tags: 标签（不推荐填写）
        :param remarks: 备注（对后续处理可以起到提示）
        :param desc: 更加详细的描述（不推荐）
        :return: int(index), bool(remind_clean)
        """
        remind_clean = False
        stuff_info = json.load(open("./backend/data/json/inbox_stuff_template.json", "r", encoding="utf-8"))
        stuff_info["name"] = name
        stuff_info["tags"] = tags
        stuff_info["remarks"] = remarks
        stuff_info["desc"] = desc
        stuff_info["createdTime"] = self.log.get_data + " " + self.log.get_formatted_time()

        self.inbox["info"]["numberOfStuff"] += 1
        if self.inbox["info"]["numberOfStuff"] > self.setting["inboxStuffLimit"]:
            remind_clean = True

        self.log.add_log("InboxManager: Add stuff-" + name, 1)
        self.inbox["stuff"].append(self.inbox["info"]["numberOfStuff"] + ".json")
        self.update_inbox_to_local(stuff_info, self.inbox_path + self.inbox["info"]["numberOfStuff"] + ".json")

        return self.inbox["info"]["numberOfStuff"], remind_clean

    def delete_stuff(self, index):

        """
        删除某个stuff
        :param index: stuff的index
        :return: bool
        """
        index = str(index)
        if index in self.inbox["stuff"]:
            self.log.add_log("InboxManager: Delete stuff-" + index, 1)

            stuff_path = self.inbox_path + index + ".json"
            self.inbox["info"]["numberOfStuff"] -= 1
            self.inbox["stuff"].remove(index)
            os.remove(stuff_path)
            self.update_inbox_to_local(None, None)
        else:
            self.log.add_log("InboxManager: Can't find stuff-" + index + " in the inbox", 3)

    def get_stuff(self, index):

        """
        获取某个stuff的信息
        :param index: stuff的index
        :return: dict
        """
        index = str(index)
        if index in self.inbox["stuff"]:
            self.log.add_log("InboxManager: Try getting stuff-" + index, 1)

            stuff_path = self.inbox_path + index + ".json"
            return json.load(open(stuff_path, "r", encoding="utf-8"))
        else:
            self.log.add_log("InboxManager: Can't find stuff-" + index + " in the inbox", 3)
            return None

    def search_stuff(self, keyword):

        """
        搜索stuff
        :param keyword: 搜索关键词
        :return:
        """

