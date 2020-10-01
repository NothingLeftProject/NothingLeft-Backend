# GettingThingsDone
- Getting Things Done is a kind of time management system which was proposed by David Allen.
- Usually, we abbreviate Getting Things Done as GTD.
- Choose language version: 
  - [EnglishVersion](./README_en.md)
  - [ChineseVersion](./README.md)

## Indroduction
- Just what I said in the top, GTD is a kind of time management system which proposed by David Allen in 2002.
- You can achieve GTD by many ways, from notebook to calendar to any planning softwares.
- But the core of us is a planning(time management) system rooted in GTD. With this system, you can achieve GTD easily and totally. More information about our project will be showed under here.

### How GTD works
- 关于这个问题，你可以在[百度百科](https://baike.baidu.com/item/GTD/7384910?fromtitle=Getting%20Things%20Done&fromid=18081892&fr=aladdin)详细了解，在这里，我只会做一些大致的介绍
- 关于GTD的理念：
  - GTD的核心理念在于只有当你把一切都安排好后，你才能心无旁骛地专心做好眼前的工作，提高效率
  - GTD认为你的压力并非来源于事情太多，而是因为你有太多事情没有做
  - GTD的目的就是要确保你所有该做的事情都做到了
  - DavidAllen认为，压力不是来自任务本身，而是任务在大脑里造成的混沌塞积。
  - 我们要做的，就是逐一清点大脑里的事务，将所有的事情都手机到大脑之外的文件系统，比如实实在在的记事簿、邮箱等，这样，你才能专心完成眼前的事情
- 关于GTD的操作方法：
  - **收集-COLLECT**
    - 就是将你所有的未尽事项（stuff）统统罗列出来，放入一个inbox中，inbox可以是任何具有记录功能的物品，但不推荐暂时性的
  - **整理-CLASSIFY**
    - 将stuff放入inbox后，你就要定期对inbox进行整理，清空它
    - 然后把这些stuff按照「可以行动」和「不可以行动」分开
    - 对于「不可以行动」中的stuff，你需要进一步对其分类，如继续分为「参考资料」「未来」「垃圾」等
    - 而对于「可以行动」中的stuff，你需要按照其能否在两分钟内完成进行操作，如果可以则立即行动，如果不可以则对其下一步行动进行「组织」
  - **组织-BUILD**
    - 组织主要分成对「参考资料的组织」和对「下一步行动的组织」
    - 对「参考资料的组织」主要就是一个文档管理系统
    - 而对「下一步行动的组织」则一般可以分为「下一步行动清单」和「追踪（等待）清单」以及「未来清单」
    - 而且如果一个行动涉及到多步骤的行动，那么你就需要将其细化成具体的行动
    - 如：写一个关于家乡文化的调查报告，那么你就需要将其分为「设计计划」「搜集资料」「整理资料」「编写文稿和PPT」等细化出来的行动
    - GTD中对「下一步行动清单」与一般的「to-do list」最大的不同就在于其进行了进一步的细化，就比如按照地点：「电脑旁」「办公室」「家」「超市」等分别记录只有在这些地方才可以执行的行动，这样等你到了这些地点的时候，你就可以一目了然地知道该做哪些工作了
  - **回顾-REVIEW**
    - 回顾也是GTD中的一个重要步骤
    - 通过回顾并检查你所有的清单，然后对它们进行鞥新，这样才能确保GTD系统的运作，而且在回顾的同时可能还需要对未来以后的行动进行计划（如果你一周回顾一次的话）
### How we works
- 那么，这个项目是如何使用，或者说工作的呢
- **交互（前端）**
  - 首先，我们需要一个可视化的交互口以便用户操作，而这种可视化的交互口是可以有很多种实现方式的。在这里，我就对一些初级阶段需要实现的交互方式进行列举和说明
    - 1、网页/WEB端：不得不说，web工具真的是很好用，轻量简洁。我个人目前考虑使用php来实现，不过我还不会php，但我会努力的，有人愿意也可以联系我一起开发
    - 2、DUEROS语音交互：通过语音交互，你可以很方便的对inbox进行整理、分类、规划等等，而DUEROS的各种设备销量都很不错，其对第三方技能开发的支持也很友善，因此我会在DUEROS上做一个技能，然后用户可以连接到公用或自己的服务器来使用
    - 3、xiaolan/wukong-robot语音交互：xiaolan和wukong-robot都是运行在各种DIY设备上的语音交互机器人，但它们与DUEROS的区别就是其都由广大开发者制作的。而其中的xiaolan就是我做的一个，虽然没有wukong厉害，但我会加油的
- **后端**
  - 很明显，后端就是支持整个软件运行的部分，其重要性显而易见
  - 那么关于后端我是打算使用python来编写的（毕竟我python很熟），而且用python做后端的软件也不少，就比如「Instagram」
  - 后端包括了「服务端」和「基本业务」
    - 服务端就是给DUEROS等更多的非自有前端（如WEB端就是自有前端）的一个接口，用户也可以根据自己的喜好，按照我们提供的API接口来开发自己喜欢的交互方式
    - 而基本业务就是最底层的部分了。基本业务其实就是完全配合GTD，再加上一些创新的实现
- 到这里，相信你已经对本项目有了一定的认识，如果您想要了解更多，请查看我们的[Wiki](https://github.com/xiaoland/GettingThingsDone/wiki)

## About

### Author
- Lan_zhijiang(This is me)
- 当然也欢迎大家来一起开发
  - Wechat：18680171381
  - QQ: 1481605673

### UpdateLog
- 完成README.md-Chinese-Version-1
