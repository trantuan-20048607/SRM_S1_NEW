# SRM 校内赛重构版框架 #

> 注：该框架为本人自用的重构魔改版，原版地址：  
> https://github.com/superwyq/robomaster_S1framework  
> 此项目为对原版的完全重构，不保证稳定性，随缘修 BUG

## 〇、使用提示 ##

### 更新记录 ###

- `2021.10.17` 添加测试模块
- `2021.10.16` 重构；添加了自定义模板
- `2021.10.9` 修复了一个严重 BUG；界面优化
- `2021.10.6` 修改了视频录制方法
- `2021.10.5` 添加分别限制显示、控制进程帧率的参数
- `2021.10.4` 添加动态准星
- `2021.10.2` 增强了 FPS 显示功能
- `2021.9.29` 修复因延迟而跳过冷却时间点
- `2021.9.28` 底盘旋转测试
- `2021.9.27` 修复大量隐藏 BUG
- `2021.9.26` 平滑过滤器改为按需运行
- `2021.9.25` 整合参数至 `/app/constants.py` 集中控制
- `2021.9.23` 优化手动瞄准性能
- `2021.9.20` 重构完成
- `2021.9.16` 魔改版本完成

### 已知问题 ###

暂未发现

### 注意事项 ###

1. （非常重要）DEBUG 模式和实机调试时所需要的控制器帧率并不相同，实机测试时调低此参数可导致图像传输卡顿；
2. 由于控制进程和界面进程先后启动，程序开始运行时会短暂延迟，调整控制器和界面帧率可缓解；
3. 使用自带自动瞄准时，由于 KALMAN 滤波器的特性，切换至 KALMAN 滤波器后目标位置会短暂漂移；

## 一、框架说明 ##

本框架为校内赛视觉部分使用框架，基于 RoboMaster S1 步兵，使用 Python 编写。

## 二、运行环境 ##

### 操作系统 ###

请尽可能在 __Windows__ + __Anaconda__ 环境中使用此框架，并且建议为此框架单独建立 Conda 环境以保持运行环境整洁：

```shell
$ conda create -n <NAME> python=3.8
```

其中 `<NAME>` 为环境名称。

> 此程序未在其他操作系统和环境中测试，不保证程序在这些环境中的稳定性和运行效果。

### Python 环境 ###

程序依赖的 Python 包列表如下：
> numpy==1.21.2  
> opencv-python==4.4.0.42  
> pygame==2.0.1  
> robomaster==0.1.1.63

在 Conda 环境中，请使用 `pip` 而非 `conda` 安装这些软件包：

```shell
$ conda activate <NAME>
$ cd <ROOT>
$ pip install -r ./requirements.txt
```

其中 `<NAME>` 为环境名称，`<ROOT>` 为框架主目录。

## 三、使用说明 ##

### 目录结构 ###

本项目对原版进行了完全重构，目录结构如下：

```
SRM_S1_NEW
├───assets   # 资源文件
│   ├───*.ttf  # 字体
│   ├───*.jpg  # 图片
│   └───*.avi  # 视频
├───app      # 主代码
│   ├───core          # 核心框架
│   │   ├───msg.py         # 消息基类
│   │   ├───container.py   # 容器类
│   │   ├───vision.py      # 图像处理函数
│   │   ├───vision_template.py  # 视觉模板
│   │   └───controller.py  # 控制器基类
│   ├───controller    # 控制器
│   │   ├───const          # 机器人参数
│   │   │   └───S1Robot         # RoboMaster S1
│   │   ├───proc.py        # 控制器进程
│   │   ├───main.py        # 功能实现
│   │   └───msg.py         # 消息封装
│   ├───benchmark     # 性能测试
│   │   ├───timer.py       # 简易计时器
│   │   └───cpu_usage.py   # 详细计时器
│   ├───test          # 逻辑测试
│   │   ├───vision.py      # 视觉测试模块
│   │   └───vision_template.py  # 视觉测试模板
│   ├───ui            # 界面
│   │   ├───proc.py        # 界面进程
│   │   ├───main.py        # 功能实现
│   │   └───msg.py         # 消息封装
│   ├───constants_template.py   # 常量模板
│   └───constants.py  # 常量定义
├───logs     # 日志
├───test.py  # 测试入口
└───main.py  # 程序入口
```

### 运行 ###

主程序通过终端开启：`python main.py`。

> 附加参数：
> - `-d, --debug` 调试模式；
> - `-r, --red` 选择红方；
> - `-b, --blue` 选择蓝方；
> - `--record` 开启录制。

### 键位与操作 ###

通过 `WSAD` 操作移动；  
按下 `Q` 开启自动瞄准、改变平滑模式；  
按下 `E` 关闭自动瞄准；  
按下 `鼠标左键` 或 `鼠标右键` 开火；  
使用自动瞄准时，按下 `R` 重设滤波器和 ROI 以消除干扰；  
使用手动瞄准时，按下 `I` 切换准星样式（十字线和圆圈）；  
按下 `Esc` 退出。

### 自定义常数 ###

所有常数配置均在文件 `/app/constants.py` 中，内附中文注释，可自行查看并修改。

### 自瞄平滑处理 ###

此框架带有自动瞄准代码，且原始自瞄数据带有大幅抖动，故此框架提供了两种平滑处理模式，分别为：

- 差分反馈（默认）：  
  前两个识别结果参与运算，并与当前结果构成三角形，根据三角形最大边长的不同划分：
    - 最大边长非常小：此时认为整个三角形都是识别结果抖动造成的，故对前两个结果附加较大的权值；
    - 最大边长适中：此时认为前两个识别结果有一部分为抖动引起，故对前两个结果附加较小的权值；
    - 最大边长较大：此时认为目标开始快速移动，对当前识别结果附加非常大的权值而几乎忽略前两个结果。

  此模式的行为受以下常数控制：
    - `TRIANGULAR_DIFFERENCE_WEIGHT`：各个划分对应的权值，其默认值为 `((1, 2, 1), (2, 2, 1), (3, 1, 0))`；
    - `TRIANGULAR_SIDE_LEN_LEVEL`：各个划分的分界线，其默认值为 `(24, 48)`。


- Kalman 滤波（备用）：  
  所有历史结果参与运算，用以预测当前结果，其行为受以下常数影响：
    - `KALMAN_SHAKE_CONTROL`：其默认值为 `1e-3`，此值越小，抖动越大，延迟越小；
    - `KALMAN_DELAY_CONTROL`：其默认值为 `1e-1`，此值越小，抖动越小，延迟越大。

### 自动瞄准测试 ###

框架自带使用 OpenCV 监控自瞄状态的测试例程，输入 `python test.py --vision --[color]` 运行测试，按 `Q` 键退出。

### 二次开发 ###

若不需要自带的自动瞄准，复制 `/app/constants_template.py` 覆盖 `/app/constants.py`， 复制 `/app/core/vision_template.py`
覆盖 `/app/core/vision.py`，参考两个模板文件的注释自行编写自动瞄准代码。若需要使用自动瞄准测试模块，复制 `/app/test/vision_template.py`
覆盖 `/app/test/vision.py` 并参考注释自行修改。

### 性能测试 ###

- 要测试某个函数的耗时，导入模块:  
  `from app.benchmark.timer import *`  
  在函数定义前一行插入修饰器 `@timer` ，运行后可在对应的日志中查看。
- 要测试某个函数内部各个行为的耗时，导入模块:  
  `from app.benchmark.cpu_usage import *`  
  在函数定义前一行插入修饰器 `@cpu_usage` ， 运行时将在控制台中显示。
