![image](https://github.com/user-attachments/assets/f988e043-9316-4c3a-a439-00988250389d)

# 🎥 bilibili_startlive.py - B 站直播一键开播 OBS 插件

该插件是一个 **基于 Python 的 OBS 脚本扩展**，用于通过调用 Bilibili 直播 API，实现 **一键开播 / 停播 + 自动配置推流地址** 的功能，适用于主播自动化流程。

---

## ✨ 功能特性

- ✅ 一键开始直播并推流至 Bilibili
- ✅ 一键停止直播并断流
- ✅ 自动配置 OBS 自定义 RTMP 地址
- ✅ UI 中支持快速跳转查看分区 ID / Cookie 教程

---

## 📦 依赖环境

本插件依赖以下 Python 模块：

| 模块          | 是否必须 | 安装方式                   |
|---------------|----------|----------------------------|
| `obspython`   | ✔️ OBS 自动注入 | OBS 脚本接口内置模块        |
| `json`        | ✔️ Python 标准库 | 无需安装                    |
| `os`          | ✔️ Python 标准库 | 无需安装                    |
| `subprocess`  | ✔️ Python 标准库 | 无需安装                    |
| `requests`    | ✔️ 必须     | `pip install requests` 安装 |

> ⚠️ 注意：你需要确保 `requests` 模块被安装到 **OBS 使用的 Python 环境** 中。

---

## 🛠 安装与使用指南

### 1. 安装 `requests` 模块（仅首次）

```bash
pip install requests
```

或指定 Python 路径：

```bash
<obs_python.exe> -m pip install requests
```

### 2. 添加脚本到 OBS

1. 打开 OBS → 工具 → 脚本
2. 点击「添加」按钮，选择本脚本 `bilibili_startlive.py`
3. 填写以下参数：
   - 房间号（room_id）
   - 分区 ID（area_id），可点击按钮查看分区表
   - 登录 Cookie，需包含 `bili_jct` 字段，可通过教程页面获取

---

## 🧪 示例：Cookie 格式

```text
SESSDATA=xxx; bili_jct=xxxxxxxxxxxxxxxxxxxxxxxx; ...
```

---

## 🚀 快速入口说明

- `🚀 开始直播并推流`：开启直播、获取推流地址、配置 OBS 并自动开播
- `🛑 停止直播并断流`：调用 API 停止直播并断开 OBS 推流
- `🔗 查看分区列表`：跳转到分区 ID API 页面
- `🔗 获取 Cookie 教程`：跳转到 B 站登录链接页面，辅助获取 cookie

---

## 🧩 技术实现说明

- 调用 `https://api.live.bilibili.com/room/v1/Room/startLive` 实现开播
- 自动提取返回 JSON 中的 RTMP 地址与推流码，并配置至 OBS
- 使用 `obspython.obs_frontend_streaming_start()` 控制 OBS 推流启动

---

## 📄 License

MIT License
