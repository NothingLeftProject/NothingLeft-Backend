# NothingLeft——A time management platform
-NothingLeft is a time management platform based on GTD concept.
-Through NothingLeft, you can make things drip-proof and arrange events in an orderly manner.
-And NothingLeft allows anyone to use its API to develop his favorite interaction method, of course, our default interaction method is WEB and voice interaction.

## Indroduction
- Getting Things Done is a kind of time management system which was proposed by David Allen.
- Usually, we abbreviate Getting Things Done as GTD.

### What is GTD:
- [Gtd-Introduction](./GTD.md)

### How we works
- So, how this project work?
- **Front**
  - First, we need to support an interfaction port for user. And this kind of visual interaction port can be implemented in many ways. Here, I will enumerate and explain some of the interaction methods that need to be implemented at the initial stage.
    - ***1, WebClient***: I have to say, the tools on web are really useful, they are simple and easy to use. I plan to use flutter to write this web UI, but I can't because I don't use JS, but I will make effort on ti. If you like to join me, please cotact me by the email under there.
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
  - DingTalk: 18680171381
  - Twitter: Lanzhijiang
  - E-mail: lanzhijiang@foxmail.com

### Usage
- Please go to [Wiki](https:/github.com/xiaoland/GettingThinsDone/wiki)
