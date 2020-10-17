# coding=utf-8
# author: Lan_zhijiang
# desciption: The code opreation memcached database
# date: 2020/10/2

import memcache


class GtdMemcachedManipulator():

    def __init__(self, log, setting, database_name="default"):

        self.log = log
        self.setting = setting
        self.database_name = database_name
        self.memcached_settings = setting["memcachedSettings"]
        
        try:
            self.memcached_server_address = self.memcached_settings["address"][database_name]
        except KeyError:
            self.log.add_log("MemcachedManipulator: Can't find memcached server named: " 
                             + database_name + "'s address in the settings, please check it.", 3)

        self.mc = memcache.Client(
            [self.memcached_server_address]
        )

    def _set(self, key, value):

        """
        设置键值（若键存在，则replace，若键不存在，则add）
        :param key 键
        :param value 值
        :return bool
        """
        if type(key) == int or type(key) == str or type(key) == float:
            self.log.add_log("MemcachedManipulator: Set: key " + str(key) + " value: " + str(value), 1)
            self.mc.set(key, value)  # Add some exception
            return True

        self.log.add_log("MemcachedManipulator: key can't be a list or dict", 3)
        return False

    def _add(self, key, value):

        """
        添加（未存在的键）的值
        :param key 键
        :param value 值
        :return bool
        """
        if type(key) == int or type(key) == str or type(key) == float:
            self.log.add_log("MemcachedManipulator: Add: key " + str(key) + " value: " + str(value), 1)
            try:
                self.mc.add(key, value)
            except self.mc.MemcachedKeyError:
                self.log.add_log("MemcachedManipulator: Add failed: there is already a key called " + str(key), 2)
                return False
            else:
                return True
                
        self.log.add_log("MemcachedManipulator: key can't be a list or dict", 3)
        return False

    def _replace(self, key, value):

        """
        替换（已存在键）的值
        :param key 键
        :param value 值
        :return bool
        """
        if type(key) == int or type(key) == str or type(key) == float:
            self.log.add_log("MemcachedManipulator: Replace: key " + str(key) + " value: " + str(value), 1)
            self.mc.replace(key, value)
            return True
            
        self.log.add_log("MemcachedManipulator: key can't be a list or dict", 3)
        return False

    def _set_multi(self, param):

        """
        设置多个键值
        :param param dict形式的数据
        :return bool
        """
        if type(param) == dict:
            self.log.add_log("MemcachedManipulator: Multi set: key to value: " + str(param), 1)
            self.mc.set_multi(param)
            return True
            
        self.log.add_log("MemcachedManipulator: In set multi, the param must be a dict!", 3)
        return False

    def _delete(self, key):

        """
        删除一个键值
        :param key: 要删除的键（同时删除了值）
        :return bool
        """
        if type(key) == int or type(key) == str or type(key) == float:
            self.log.add_log("MemcachedManipulator: Delete: key: " + str(key), 1)
            self.mc.delete(key)
            return True
            
        self.log.add_log("MemcachedManipulator: key can't be a list or dict", 3)
        return False

    def _delete_multi(self, param):

        """
        删除多个键值
        :param param: 要删除的键的list
        :return bool
        """
        if type(param) == list or type(param) == tuple:
            self.log.add_log("MemcachedManipulator: Delete: keys: " + str(param), 1)
            self.mc.delete_multi(param)
            return True
            
        self.log.add_log("MemcachedManipulator: In delete multi, param must be a list", 3)
        return False

    def _get(self, key):

        """
        获取键的值
        :param key 键
        :return any
        """
        if type(key) == int or type(key) == str or type(key) == float:
            self.log.add_log("MemcachedManipulator: Get: key: " + str(key), 1)
            try:
                return self.mc.get(key)
            except self.mc.MemcachedKeyError:
                self.log.add_log("MemcachedManipulator: key: " + str(key) + "not found!", 3)
                return None
            
        self.log.add_log("MemcachedManipulator: key can't be a list or dict", 3)
        return None

    def _get_multi(self, param):

        """
        获取多个键的值
        :param param: 要获取的键的list
        :return any
        """
        if type(param) == list or type(param) == tuple:
            self.log.add_log("MemcachedManipulator: Get multi: keys: " + str(param), 1)
            return self.mc.get_multi(param)
        
        self.log.add_log("MemcachedManipulator: key can't be a list or dict", 3)
        return None

    def _increase(self, key):

        """
        key的值自加
        :param key 键
        :return bool
        """
        if type(key) != int or type(key) != str or type(key) != float:
            self.log.add_log("MemcachedManipulator: key can't be a list or dict", 3)
            return False

        self.log.add_log("MemcachedManipulator: Self increase: key: " + str(key), 1)
        self.mc.incr(key)
        return True

    def _decrease(self, key):

        """
        key的值自加
        :param key 键
        :return bool
        """
        if type(key) != int or type(key) != str or type(key) != float:
            self.log.add_log("MemcachedManipulator: key can't be a list or dict", 3)
            return False

        self.log.add_log("MemcachedManipulator: Self decrease: key: " + str(key), 1)
        self.mc.decr(key)
        return True

    def return_mc(self):

        """
        返回连接着的memcached数据库操作class
        :return class
        """
        return self.mc

    def disconnect(self):

        """
        断开当前连接的memcached数据库
        :return
        """
        self.mc.disconnect_all()

    def connect_to_new(self, database_name):

        """
        连接到新的memcached数据库
        :return 
        """
        self.disconnect()
        self.database_name = database_name
        try:
            self.memcached_server_address = self.memcached_settings["address"][database_name]
        except KeyError:
            self.log.add_log("MemcachedManipulator: Can't find memcached server named: " 
                             + database_name + "'s address in the settings, please check it.", 3)

        self.mc = memcache.Client(
            [self.memcached_server_address]
        )
        
