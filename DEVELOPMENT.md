# 运行与维护

## 安装包

- [0.1 原版恢复包](https://github.com/iyau76/Nvshu-Learning-App/releases/tag/v0.1-recovered)：找回的原始 Android 安装包，保留原始 debug 签名。
- 0.2.0 维护候选包：修复多选返回后的选择显示、复盘错答历史、长选项换行与答题后文字亮度，修复设置布局和数据保存。桌面已验证，Android 实机验收待完成。

包名继续使用 `org.kivy.nvshuapp`。本次本机构建沿用原有签名，versionCode 从 10211 增为 10212。自行构建所用的 debug 密钥可能不同；已有安装的覆盖升级取决于签名一致性。

## 桌面运行

Python 3.11 或 3.12：

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

进度与设置保存在 Kivy `App.user_data_dir`。Windows 默认是 `%APPDATA%\nvshu`，Android 使用应用私有 files 目录。测试可用环境变量 `NVSHU_DATA_DIR` 指向临时目录。

第一次读取会兼容旧源码目录下的 `data/progress` 与 `state/settings.json`，首次成功保存写入新目录。安装包中不再混入开发者进度。旧版把进度放在解包目录中，Android 覆盖升级时旧解包内容能否保留尚未实机确认。

```sh
python -m pip install pytest
python -m pytest tests -q
# 无桌面的 Linux: xvfb-run -a python -m pytest tests -q
```

## Android 构建

使用 Ubuntu / WSL，在 Linux 文件系统中放置项目。需要 JDK 17、Buildozer 1.5.0、Cython 0.29.36，以及 Buildozer 所需的系统编译依赖。安装指引见 [Buildozer 官方文档](https://buildozer.readthedocs.io/en/latest/installation.html)。

```sh
python3 -m pip install --user buildozer==1.5.0 Cython==0.29.36
bash scripts/build-android.sh
```

`buildozer.spec` 固定 python-for-android 提交与 Kivy 版本，移除了特定用户的 NDK 绝对路径。本轮沿用 API 31、最低 API 21、NDK 28c 及两种 ARM 架构。产物位于 `bin/`。

本次成功构建复用了 2025 年保留的 Python/SDL2 原生编译缓存，再打包维护后的应用源码；没有宣称完成从空缓存重建。签名密钥保留在本机，未进入仓库。

## 内容与验证

题库、解析、字体、图片与研究材料保持原样。`tests/content.sha256.json` 记录题库及素材的原始摘要，回归测试检查是否发生意外修改。

桌面回归覆盖：多选返回状态、两次答对与复习模式、历次错答复盘、设置损坏、进度损坏备份、原子保存失败、首次读取只读兼容、答题保存失败重试、真实窗口布局及返回/暂停处理。GitHub Actions 会运行同一组回归并保存界面截图。

Android 当前已完成：APK 构建、签名验证、包名与版本检查、包内题库/字体/字节码核验。尚无安卓实机安装、启动和覆盖升级证据。主菜单“测试（开发中）”维持原有功能范围。
