# 1.明确需求
# 明确采集的网站以及数据内容
# 网址:https://music.163.com/#/song?id=2080527930(任意一首歌链接)
# 数据。评论信息
# 2.抓包分析
# 通过浏览器的开发者工具分析对应的数据位置
# 打开开发者工具
# 刷新网页
# 通过关键字搜过找到对应的数据位置
# post 需要在载荷中去查看，有些被加密了
import csv
from datetime import datetime
from pathlib import Path

import requests

# 导入执行 js 代码模块（本地兼容层 execjs.py，底层用 node 跑）
import execjs


def get_post_data(pageNo, hursor):
    SONG_ID = "1413585838"
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36 Edg/156.0.0.0"),
        "Cookie": "",          # 需要登录态时再填，公开接口不用
        "Referer": f"https://music.163.com/#/song?id={SONG_ID}",
    }
    url = ("https://music.163.com/weapi/comment/resource/comments/get" 
           "?csrf_token=fec364ed9e4ed92113a1da282203d890")

    # 调 JS 算签名（一次编译，反复调用）
    data = ctx.call("get_post_data", pageNo, hursor,SONG_ID)

    res = requests.post(url=url, headers=headers, data=data, timeout=30)
    res.raise_for_status()
    resp = res.json()

    payload = resp.get("data") or {}
    # 热评只有第一页有；普通评论每页都有
    comments = (payload.get("hotComments") or []) + (payload.get("comments") or [])

    for i in comments:
        dc = i.get("time")
        dt = str(datetime.fromtimestamp(int(dc / 1000))) if dc else ""

        ip = i.get("ipLocation")
        location = ip.get("location", "") if isinstance(ip, dict) else (ip or "")

        writer.writerow({
            "用户名": (i.get("user") or {}).get("nickname", ""),
            "内容": (i.get("content") or "").replace("\n", " "),
            "地区": location,
            "日期": dt.split(" ")[0] if dt else "",
            "时间": dt.split(" ")[1] if dt else "",
        })
        print()

    print(f"  第 {pageNo} 页：{len(comments)} 条")
    # 提取下一页参数
    next_page = resp["data"]["cursor"]
    return next_page


# 编译 js 代码（只编译一次，放在函数外）
BASE_DIR = Path(__file__).parent
js_code = (BASE_DIR / "网易逆向评论.js").read_text(encoding="utf-8")
ctx = execjs.compile(js_code)

# 打开 CSV（全程只打开一次，最后统一关闭）
f = open(BASE_DIR / "评论.csv", "w", encoding="utf-8-sig", newline="")
writer = csv.DictWriter(f, fieldnames=["用户名", "内容", "地区", "日期", "时间"])
writer.writeheader()

hursor = ""                       # 第一页 cursor 传空
for t in range(1, 21):
    print(f"正在爬取第{t}页的数据")
    hursor = get_post_data(str(t), hursor)

f.close()
print("完成，结果见 评论.csv")

# 分析请求参数/链接的变化规律
# 链接是一样的,主要变化的请求参数:params/encSecKey
# 看不出变化规律，分析参数如何生成的就行了:
# 1.搜值/键名 -> 看是否存在其他的数据包返回
# 2.逆向 ->参数无缘无故生成,肯定有来源，基本是都是通过js代码进行生成
# 定位加密位置
# 通过关键字搜索定位/启动器跟栈分析:调用的就三个:@music/inject/core

# 去网易逆向评论看
