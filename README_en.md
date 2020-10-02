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
- About this question, you can know more on [Wikipedia](https://en.wikipedia.org/wiki/Getting_Things_Done). I will only make some simply introduction here.
- The core of GTD：
  - GTD's core thinks that only when you arrage everything well, you can focus on what you going to do and improve your effectiveness.
  - GTD thinks your stress is not because there are too many things to do, but because you have too many things didn't do.
  - So, the purpose of GTD is to make sure the things you need to do had been all finished.
  - And, David Allen thinks, the stress is not from task itself, but the messes causes by the tasks remain in your brain.
  - The things we have to do is to list the tasks in our brain into a file system which out of your brain, such as real notebook, e-mail, etc. Then, you can focus on what you have to do now. 
- The opreation method of GTD：
  - **COLLECT**
    - It is to list all the unfinished things(called as stuff) and put them into an inbox.
    - Inbox can be anything which can recording, but it not recommend you use a temporary thing.
  - **CLASSIFY**
    - After you put those(stuff) into the inbox, you need to sort them out regularly.
    - Then you should classify these stuffs according to "can take action" and "can't take action"
    - To those stuffs in "can't take action", you need to further classify them. Such as "data", "someday/future" and "trash".
    - And to those stuffs in "can take action", you need to classify them according to can it be finished in two minutes. If can, you should take action right now. If not, you can plan the next action of it.
  - **ORGANIZE**
    - Organizations are mainly divided into "organization of data" and "organization of next actions"
    - For "organization of data" is mainly like a file management system.
    - And for "organization of net actions" can divided into "next actions list" and "future/someday list".
    - And if an action connect to many actions, then you need to refine it into specific actions.
    - For example, if you are going to write a report about your hometown, that means you need to divided it into "Planning", "Picking", "Classify", "Make powerpoint and document"...and some specific actions.
    - GTD中对「下一步行动清单」与一般的「to-do list」最大的不同就在于其进行了进一步的细化，就比如按照地点：「电脑旁」「办公室」「家」「超市」等分别记录只有在这些地方才可以执行的行动，这样等你到了这些地点的时候，你就可以一目了然地知道该做哪些工作了
  - **REVIEW**
    - 回顾也是GTD中的一个重要步骤
    - 通过回顾并检查你所有的清单，然后对它们进行鞥新，这样才能确保GTD系统的运作，而且在回顾的同时可能还需要对未来以后的行动进行计划（如果你一周回顾一次的话）
### How we works
- So, how this project work?
- **Front**
  - First, we need to support an interfaction port for user. 
  - 首先，我们需要一个可视化的交互口以便用户操作，而这种可视化的交互口是可以有很多种实现方式的。在这里，我就对一些初级阶段需要实现的交互方式进行列举和说明
    - 1、网页/WEB端：不得不说，web工具真的是很好用，轻量简洁。我个人目前考虑使用php来实现，不过我还不会php，但我会努力的，有人愿意也可以联系我一起开发
    - 2、DUEROS语音交互：通过语音交互，你可以很方便的对inbox进行整理、分类、规划等等，而DUEROS的各种设备销量都很不错，其对第三方技能开发的支持也很友善，因此我会在DUEROS上做一个技能，然后用户可以连接到公用或自己的服务器来使用
    - 3、xiaolan/wukong-robot语音交互：xiaolan和wukong-robot都是运行在各种DIY设备上的语音交互机器人，但它们与DUEROS的区别就是其都由广大开发者制作的。而其中的xiaolan就是我做的一个，虽然没有wukong厉害，但我会加油的
- **Backend**
  - 很明显，后端就是支持整个软件运行的部分，其重要性显而易见
  - 那么关于后端我是打算使用python来编写的（毕竟我python很熟），而且用python做后端的软件也不少，就比如「Instagram」
  - 后端包括了「服务端」和「基本业务」
    - 服务端就是给DUEROS等更多的非自有前端（如WEB端就是自有前端）的一个接口，用户也可以根据自己的喜好，按照我们提供的API接口来开发自己喜欢的交互方式
    - 而基本业务就是最底层的部分了。基本业务其实就是完全配合GTD，再加上一些创新的实现
- 到这里，相信你已经对本项目有了一定的认识，如果您想要了解更多，请查看我们的[Wiki](https://github.com/xiaoland/GettingThingsDone/wiki)

## About

### Author
- Lan_zhijiang(That's me)
- Of course, everyone is welcome to develop together.
  - Wechat：18680171381
  - Twitter: Lanzhijiang
  - E-mail: lanzhijiang@foxmail.com

### Usage
- Please go to [Wiki](https:/github.com/xiaoland/GettingThinsDone/wiki)
