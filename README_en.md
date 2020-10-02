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
- About this topic, you can go to [Wikipedia](https://en.wikipedia.org/wiki/Getting_Things_Done). I will only make some simply introduction here.
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
    - The biggest difference between the "next actions list" and the general "to-do list" in GTD is that it has been further refined, according to the following locations: "next to the computer", "office", "home", "supermarket", etc. Record the actions that can only be performed in these places, so that when you get to these places, you can know at a glance that you need to do some work.
  - **REVIEW**
    - Review
    - Review is also an important step in GTD.
    - By reviewing and checking all your lists, and then updating them, in order to ensure the operation of the GTD system, and while reviewing, you may also need to plan for future actions (if you review once a week)
### How we works
- So, how this project work?
- **Front**
  - First, we need to support an interfaction port for user. And this kind of visual interaction port can be implemented in many ways. Here, I will enumerate and explain some of the interaction methods that need to be implemented at the initial stage.
    - ***1, WebClient***: I have to say, the tools on web are really useful, they are simple and easy to use. I plan to use php to write this web client, but I can't because I don't use php, but I will make effort on ti. If you like develop with me, please cotact me by the email under there.
    - ***2, Dueros/AmazonEcho***: According to speech interfaction, you can do anything to inbox such as planning easily. I will develop a skill on them(dueros and amazon echo) so that you can use this event.
      - Tips: Dueros is same as the Amazon Echo, But Dueros works in a Chinese environment.
    - ***3, xiaolan/wukong-robot***: xiaoland and wukong-robot are a smart robot which can run on raspberrypi. Both of them are public on github, you can search them to get more info. And xiaolan is develop by me, although it not great than wukong-robot, but I will keep working hard.
- **Backend**
  - Obviously, the backend is the part that supports the operation of the entire software, and its importance is obvious.
  - So, about the backend, I plan to use python to write (after all I am very familiar with python), and there are a lot of software using python as the backend, such as "Instagram"
  - It includes "server" and "base"
    - The server is an interface for more non-own front such as Dueros (web client is its own front end). Users can also develop their own interaction according to their own preferences and according to the API interface we provide.
    - The "base" is the most basic part. The "base" is actually fully compatible with GTD, but will also add some new ideas.
- At this point, I believe that you have a certain understanding of this event, if you want to know more, please go to our [Wiki](https://github.com/xiaoland/GettingThingsDone/wiki)

## About

### Author
- Lan_zhijiang(That's me)
- Of course, everyone is welcome to develop together.
  - Wechat：18680171381
  - Twitter: Lanzhijiang
  - E-mail: lanzhijiang@foxmail.com

### Usage
- Please go to [Wiki](https:/github.com/xiaoland/GettingThinsDone/wiki)
