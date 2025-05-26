# -*- coding: utf-8 -*-
# bilibili_startlive.py - 简化版 OBS 插件，控制 B 站开播 / 停播 + 自动设置推流地址

import obspython
import json
import requests
import os
import subprocess

# ===== 全局变量 =====
room_id = ''
area_id = 610
cookie = ''



def open_url(url: str):
    """使用非阻塞方式打开链接，避免卡顿"""
    try:
        if os.name == 'nt':
            subprocess.Popen(
                ['cmd', '/c', 'start', '', url],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            subprocess.Popen(
                ['xdg-open', url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except Exception as e:
        print(f"[open_url 错误] 无法打开链接 {url}: {e}")


def open_bilibili_area(props, prop):
    open_url("https://api.live.bilibili.com/room/v1/Area/getList?show_pinyin=1")

def open_bilibili_cookie(props, prop):
    open_url("https://link.bilibili.com/")

# ===== B 站开播 / 停播接口 =====
def startLive(csrf: str, area_id: int, room_id: str, cookie: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie
    }
    data = {
        "room_id": room_id,
        "platform": "mobile",
        "area_v2": area_id,
        "backup_stream": 0,
        "csrf_token": csrf,
        "csrf": csrf,
    }

    resp = requests.post(
        "https://api.live.bilibili.com/room/v1/Room/startLive",
        data=data,
        headers=headers
    )

    print("[startLive] 状态码:", resp.status_code)
    print("[startLive] 返回文本前 300 字：", resp.text[:300])

    if not resp.text.strip().startswith('{'):
        raise Exception("[startLive 错误] 返回非 JSON")
    resp_d = resp.json()
    if resp_d.get('code') != 0:
        raise Exception(f"[startLive 接口错误] {resp_d}")
    return resp_d

def stopLive(csrf: str, room_id: str, cookie: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie
    }
    data = {
        "room_id": room_id,
        "platform": "pc",
        "csrf_token": csrf,
        "csrf": csrf,
    }

    resp = requests.post(
        "https://api.live.bilibili.com/room/v1/Room/stopLive",
        data=data,
        headers=headers
    )

    print("[stopLive] 状态码:", resp.status_code)
    print("[stopLive] 返回文本前 300 字：", resp.text[:300])

    if not resp.text.strip().startswith('{'):
        raise Exception("[stopLive 错误] 返回非 JSON")
    resp_d = resp.json()
    if resp_d.get('code') != 0:
        raise Exception(f"[stopLive 接口错误] {resp_d}")
    return resp_d

# ===== OBS 推流设置 =====
def set_service(server: str, key: str):
    cfg = json.dumps({'server': server, 'key': key})
    settings = obspython.obs_data_create_from_json(cfg)

    service = obspython.obs_service_create('rtmp_custom', 'rtmp', settings, None)
    obspython.obs_frontend_set_streaming_service(service)

    obspython.obs_service_release(service)
    obspython.obs_data_release(settings)

# ===== 按钮事件处理 =====
def handle_start(props, prop):
    global cookie, room_id, area_id

    cookie_clean = cookie.strip().replace('\n', '')
    csrf = ''
    for kv in cookie_clean.replace(' ', '').split(';'):
        if kv.startswith('bili_jct='):
            csrf = kv.split('=', 1)[1]
    if not csrf:
        raise Exception("Cookie 中缺少 bili_jct 参数")

    print("[开始直播] 正在发起请求...")
    result = startLive(csrf, area_id, room_id, cookie_clean)
    addr = result['data']['rtmp']['addr']
    code = result['data']['rtmp']['code']

    print(f"[推流设置] RTMP 地址: {addr}")
    print(f"[推流设置] 推流码: {code}")

    set_service(server=addr, key=code)
    obspython.obs_frontend_streaming_start()

def handle_stop(props, prop):
    global cookie, room_id

    cookie_clean = cookie.strip().replace('\n', '')
    csrf = ''
    for kv in cookie_clean.replace(' ', '').split(';'):
        if kv.startswith('bili_jct='):
            csrf = kv.split('=', 1)[1]
    if not csrf:
        raise Exception("Cookie 中缺少 bili_jct 参数")

    stopLive(csrf, room_id, cookie_clean)
    obspython.obs_frontend_streaming_stop()

# ===== OBS 插件接口实现 =====
def script_description():
    return '🔴 B 站开播控制插件 - 自动推流设置 + 快速开关播'

def script_update(settings):
    global cookie, room_id, area_id
    cookie = obspython.obs_data_get_string(settings, 'cookie')
    area_id = obspython.obs_data_get_int(settings, 'area_id')
    room_id = obspython.obs_data_get_string(settings, 'room_id')

def script_properties():
    props = obspython.obs_properties_create()

    obspython.obs_properties_add_text(props, "room_id", "📺 房间号 Room ID", obspython.OBS_TEXT_DEFAULT)
    obspython.obs_properties_add_int(props, "area_id", "🗂 分区 ID Area ID", 0, 10000, 1)
    obspython.obs_properties_add_button(props, "area_help", "🔗 查看分区列表", open_bilibili_area)

    obspython.obs_properties_add_text(props, "cookie", "🍪 登录 Cookie（含 bili_jct）", obspython.OBS_TEXT_DEFAULT)
    obspython.obs_properties_add_button(props, "cookie_help", "🔗 获取 Cookie", open_bilibili_cookie)

    obspython.obs_properties_add_button(props, "start_live", "🚀 开始直播并推流", handle_start)
    obspython.obs_properties_add_button(props, "stop_live", "🛑 停止直播并断流", handle_stop)

    return props
