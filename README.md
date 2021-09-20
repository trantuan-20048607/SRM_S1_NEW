# SRM 校内赛重构版框架 #

> 注：该框架为本人自用的重构魔改版，原版地址：  
> https://github.com/superwyq/robomaster_S1framework  
> 此项目为对原版的完全重构，不保证稳定性，随缘修 BUG

## 〇、更新记录 ##

- `2021.9.20` 重构完成
- `2021.9.16` 魔改版本完成

## 一、框架说明 ##

此部分内容和原版一致。
> 本框架为校内赛视觉部分使用框架，基于 Robomaster S1 步兵，使用 Python 编写。

## 二、环境依赖 ##

魔改版框架和原版框架所需依赖没有任何区别，具体依赖如下：
> pillow==8.3.2  
> numpy==1.21.2  
> opencv-python==4.4.0.42  
> pygame==2.0.1  
> robomaster==0.1.1.63

在 requirements.txt 中列出了相同内容。

## 三、使用说明 ##

### 目录结构 ###

本项目对原版进行了完全重构，目录结构如下：

```
SRM_S1_NEW
├───assets   # 资源文件
│   ├───*.ttf       # 字体
│   ├───*.jpg       # 图片
│   └───*.avi       # 视频
├───app      # 主代码
│   ├───core        # 核心框架
│   │   ├───msg.py         # 消息基类
│   │   ├───container.py   # 容器类
│   │   ├───vision.py      # 图像处理函数
│   │   └───controller.py  # 控制器基类
│   ├───controller  # 控制器
│   │   ├───proc.py        # 控制器进程
│   │   ├───main.py        # 功能实现
│   │   └───msg.py         # 消息封装
│   └───ui          # 界面
│       ├───proc.py        # 界面进程
│       ├───main.py        # 功能实现
│       └───msg.py         # 消息封装
├───logs     # 日志
├───tmp      # 临时输出
└───main.py  # 程序入口
```

### 运行 ###

主程序通过终端开启：`python main.py`

> 参数:
> - `-d --debug` 调试模式
> - `-r --red` 选择红方
> - `-b --blue` 选择蓝方
> - `-v --video` 录制视频
>
> 注：调试模式激活时无法录制视频。

### 键位与操作 ###

通过`WASD`操作移动；  
按下`Q`开启瞄准，`E`关闭瞄准；  
按下`Esc`退出。
