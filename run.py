# coding=utf-8
# author: Lan_zhijiang
# description: system run
# date: 2020/12/19

from backend.init import BackendInit

backend_init = BackendInit()

if __name__ == "__main__":
    backend_init.run_backend()
