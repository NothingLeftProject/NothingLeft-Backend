# 用户系统-UserSystem
- 用户系统是一个非常关键的部分，它的存在使得NL成为一个平台，而不是一个私人软件
  - 打个比方：因为用户系统的存在，NL允许一个机构在一台服务器上运行NL就可以使得机构中的所有人都不必自己搭建一个NL
- 同时，用户系统还管理着API的权限，从而保证了多用户的可行性

## 组成部分-Includes
- 用户系统不是一个独立的文件，而是一个系统，它由多个部分共同协调组成

### **1、UserManager**
  - UserManager（用户管理器），最基本的部分，他管理着用户的注册、登录、登出等简单的，不涉及复杂信息修改的操作
  - 位于：/backend/user/user_manager.py 中的 UserManager(class)
  - 点击[UserManager](user_manager.md)查看详细说明
  
        
