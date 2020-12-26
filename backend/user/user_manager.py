# coding=utf-8
# author: Lan_zhijiang
# description: 用户管理器
# date: 2020/10/2

import json
from backend.data.encryption import Encryption
from backend.database.mongodb import MongoDBManipulator
from backend.user.user_info_operator import UserInfoManager
from backend.user.user_group_manager import UserGroupManager


class UserManager:

    def __init__(self, log, setting):

        self.log = log
        self.setting = setting

        self.encryption = Encryption(log, setting)
        self.mongodb_manipulator = MongoDBManipulator(log, setting)
        self.user_group_manager = UserGroupManager(log, setting)
        self.user_info_manager = UserInfoManager(log, setting)

    def sign_up(self, account, password, email, user_group="user"):

        """
        注册用户
        :param account: 账户名
        :param password: 密码(md5)
        :param email: 电子邮箱
        :param user_group: 用户组
        :return bool
        """
        if "/" in account or "." in account or "-" in account:
            self.log.add_log("UserManager: '/', '.' and '-' is banned in account name", 3)
            return False, "account not in law"

        if self.mongodb_manipulator.is_collection_exist("user", account) is True:
            self.log.add_log("UserManager: Sign up fail, this user had already exists. sign up account: " + account, 3)
            return False, "user had already exists"

        if self.mongodb_manipulator.add_collection("user", account) is False:
            self.log.add_log("UserManager: Sign up failed, something wrong while add account. sign up account: " + account, 3)
            return False, "add user went wrong"
        else:
            self.log.add_log("UserManager: Account add to the collection: user successfully", 1)

        password = self.encryption.md5(password)

        user_info = json.load(open("./backend/data/json/user_info_template.json", "r", encoding="utf-8"))
        user_info[0]["account"] = account
        user_info[1]["password"] = password
        user_info[2]["email"].append(email)
        user_info[4]["userGroup"] = user_group
        if self.mongodb_manipulator.add_many_documents("user", account, user_info) is False:
            self.log.add_log("UserManager: Sign up failed, something wrong while add user info. sign up account: " + account, 3)
            return False, "add info went wrong"
        else:
            self.user_group_manager.add_user_into_group(account, user_group)
            self.log.add_log("UserManager: Sign up success", 1)
            return True, "success"

    def delete_user(self, account):

        """
        删除某个用户
        :param account: 账户名
        :return:
        """
        self.log.add_log("UserManager: Delete user: " + account, 1)
        if self.mongodb_manipulator.is_collection_exist("user", account) is False:
            self.log.add_log("UserManager: delete fail, this user does not exists. sign up account: " + account, 3)
            return False, "user does not exists"
        
        if self.mongodb_manipulator.delete_collection("user", account) is False:
            return False, "database error"
        else:
            return True, "success"

    def login(self, account, password):

        """
        登录
        :param account: 账户
        :param password: 密码
        :return: bool(fail) str(success)
        """
        self.log.add_log("UserManager: Try login " + account, 1)

        user_info, res = self.user_info_manager.get_one_user_multi_info(account, ["password", "avatar"])
        if user_info is False:
            self.log.add_log("UserManager: login: Can't find your account or something wrong in the mongodb or user not exist.", 3)
            return False, "database error or user not exist"
        else:
            if password == user_info["password"]:
                token = self.encryption.md5(self.log.get_time_stamp() + account)

                self.mongodb_manipulator.update_many_documents("user", account, {"_id": 7}, {"token": token})
                self.setting["user"]["account"] = account
                self.setting["user"]["avatar"] = user_info["avatar"]  # needs a solution

                # add user group manager to get permission

                self.log.add_log("UserManager: login success", 1)
                return token, "success"
            else:
                self.log.add_log("UserManager: Your password is wrong", 1)
                return False, "passwordWrong"

    def logout(self, account):

        """
        登出（竟然给忘了）
        :param account: 要登出的账户名
        :return:
        """
