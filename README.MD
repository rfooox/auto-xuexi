# auto-xuexi
> 自动进行当日学习
## 0 如何使用
### 0.1 使用adb工具连接手机


## 1 功能规划
### 1.1 判断当前页面
### 1.2 获取积分情况
### 1.3 自动视频学习
### 1.4 自动收集题库
### 1.5 自动答题

## 2 技术选型
1. python 3.9.6
2. uiautomator2 2.16.19
3. peewee 3.15.2
4. sqlite
5. 学习强国 2.41.0(15482150)
6. adb-tools()
7. weditor 0.6.5


## 3 环境准备
### 3.1 adb安装
adb 全称 `Android Debug Bridge` 通过adb工具方便获取Android设备的
[adb 下载](https://developer.android.google.cn/studio/releases/platform-tools?hl=zh-cn)
#### 3.1.1 macbook adb安装
先安装homebrew，在终端中输入 `brew install android-platform-tools` 安装

### 3.2 python 组件安装
#### 3.2.1 python 安装
访问python网站，下载对应系统的安装包，按照安装程序提示安装即可。
[python 下载](https://www.python.org/downloads/release/python-396/)
#### 3.2.2 python包安装
程序依赖`uiautomator2`、`peewee`这两个包，开发测试版本如下，若无法正常安装可以尝试其它版本。

`weditor`工具非必须依赖，方便获取`xpath`可以更直观的调试。
```shell
pip install -U uiautomator2==2.16.19
pip install -U peewee==3.15.2
pip install -U weditor==0.6.5
```

## 4 更新开发计划与状态
> 当前版本：v0.0.1

自动更新题库的功能已经完成，

TODO LIST：
1. 控制远程adb终端
2. 加入日志模块
3. 优化日志输出
4. 提示答题
5. 自动答题
6. 设置自动答题上限
7. 自动刷视频
8. 自动阅读文章
9. 自动查看积分信息选择对应项目

### 版本号：v0.0.1
> 【init】首次更新
#### 计划功能
1. 可正常读取数据线连接手机
2. 适配机型：Huawei Nova
3. 程序框架基本建成
4. 完成题库收集能力，自动纠错功能完善
#### 已知问题
1. 数据库计数字段初始化错误
2. `update_time` 更新时间字段更新异常
3. 题目相同会随机打乱顺序导致数据库题数激增

### 版本号：v0.0.2
> 【debug】修复部分缺陷
#### 计划修复
1. 题目相同会随机打乱顺序导致数据库题数激增