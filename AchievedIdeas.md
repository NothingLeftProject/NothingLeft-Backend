# AchievedIdeas
- 这里是READEME.md中想法区已经完成的想法的归档处

### inbox的清空操作（归档！）
- 即从preset_list中删除归档了的stuff的id
- 并添加其id到achievedStuffs中去
- 并修改stuff_info中的isAchieved为True

### 节省资源开销
- 从init加载一个base_ability类像log一样传递下去

### stuff等同类型事务的本地创建性
- 注意！因为API的验证设置，必须要使请求时间戳与本地同步误差在5min以内
  - 但同时，stuff等此类的事务的createDate和LastOperateTimeStamp仍然需要按照客户端本地时间，这是为了用户的体验所必须的
  
### 使用update_document直接更新document中的变更的key值以优化性能

### 将一直以来缺少的lastOperateTimeStamp的修改都加上（函数特化）

### ERROR: 判断stuff之类的存不存在之后再添加，但忘了判断这个stuff是否已经存在于原来的列表中