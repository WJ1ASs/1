# 网易云音乐：抓榜单 → 逐首签名 → 下载音频
#
# 用法：
#   python 18-逆向js网易云音乐歌曲.py          # 默认前 5 首
#   python 18-逆向js网易云音乐歌曲.py 10       # 前 10 首
#
# 想下 VIP 歌曲：先在终端设置环境变量 MUSIC_COOKIE（从浏览器复制的完整 cookie），
# 例如  set MUSIC_COOKIE=xxx（cmd）或 $env:MUSIC_COOKIE="xxx"（PowerShell）
import os
import re
import sys
from pathlib import Path

import execjs
import requests

# ============ 配置 ============
MAX_SONGS = int(sys.argv[1]) if len(sys.argv) > 1 else 200
LIST_URL = "https://music.163.com/discover/toplist?id=3778678"
API = "https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token="
BASE_DIR = Path(__file__).parent
OUT_DIR = BASE_DIR / "music"

H = {
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36 Edg/156.0.0.0"),
    "referer": "https://music.163.com/",
}
# ============ Cookie 填这里（就这一行）============
# 把浏览器复制的整串 cookie 粘到下面两个引号之间，例如：
#   COOKIE = "_ga=GA1.1...; MUSIC_U=00FCD5...; __csrf=fec364ed..."
# 留空就只能下免费歌；也可以改用环境变量 MUSIC_COOKIE
COOKIE = "_ga=GA1.1.39729424.1786735311; _ga_EPDQHDTJH5=GS2.1.s1786735310$o1$g0$t1786735351$j19$l0$h0; _iuqxldmzr_=32; _ntes_nnid=134daf1880f8f8cc5d5ea067d5b43779,1792992003720; _ntes_nuid=134daf1880f8f8cc5d5ea067d5b43779; NMTID=00Ot5NhVqUyu8L0ckU3rw7DlhOoC2cAAAGhdqa__Q; WEVNSM=1.0.0; WNMCID=kteecc.1792992004922.01.0; WM_TID=AixjKi8JjDhEVRBVRFfJRi9o2XygG1uq; ntes_utid=tid._.hB3SVu%252Fsl61BEwVFQRfJFm4tzGmkdv6M._.0; sDeviceId=YD-13sBCg9JGM9EQhRQQRfNFyoonCm1dvqZ; __snaker__id=Jf4t11w0U8lqKrFh; ntes_kaola_ad=1; WM_NI=ZFoEC1VADiAy%2FlzDCduGCxfgboshOqFxHiRzL0xpVhK7jjhPiS0E6W7NUkBn4XJFbRJdWxODnnZVR7MPqzX5h09AdTADKj5LIoh2t2WmIyGKcrrqgkLSkNRkzfQEzsfcQVU%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeb1d944ba8cbe89b872b5968eb2c85f829a9fb0e74faff58586c74d8e95a5b3c12af0fea7c3b92a9a9aa1a6c23b969f8c8ac473edb4b6a5c270b7998d99e56da2b1bd89ce7b86a8888ad17290f0b891d56489e9a68beb5cab8d00a6b55df5929b8cc166f88886a7e15a8abc9999ce50aeb296b7d13d8f90bf9bdb3facf0f7a2e760839c858bb8488bb1a8d3f73a95b3879ac641a1aebe92e661908da5afd161baba9fa6f979a6bd9fb7d837e2a3; Hm_lvt_1483fb4774c02a30ffa6f0e2945e9b70=1793005523,1793071559,1793080383,1793095459; HMACCOUNT=FD24C7614125E56E; gdxidpyhxdE=MDJuI%2Fsu7ye9KOVZZxlJz5a9NvOO7HE7emYeijjv2bEYzRmXWYQ4Bj0LYOlQCwj46hNxRzAxZGIjam6JbWH%2Bim5WEUEts7ktIWyrZN85lKvUxSATccfg1xnSXY3vvl1g4Cww%2FxNQqa86%2BVMvJorhMuSHTVWrk7ETPdccUJiayzaGBSR6%3A1793096445308; __csrf=fe6e7eb4ffa467b20277246bdb9a7b9c; MUSIC_U=007A218FBE649C921611FCFEE593987B15AA8CFF8343C3059D32D2C087B6A61D6A4D8B2361F39F79800E5624403DF26453083031B749904BC81DBAE599C7651C741EEC257A19AB58FC32FCEB5113E95A03AE5DE73858A64CBF5C476FB5DF031FE77150EEB5209A0D84345CDCC8E3BCB6F551A22143E36E315EF57A517F1CA816B7A571F91788AE3C01C0C7F9897CA31F6EF56C04871A46FB179B802FAADE06A09508E6EF4D9F26AB7B4555E4EFE6B5AEB0ECF6344F5D219ADA713EA49FB580419AB8911A5825A19EAEC09A8A76206C912EF86188C9DF70543C6B00482172A2461A8E750EEFB37BFD2CCF7C53F4F91E9989110F96D61B1F6C6A9FBE4170130EC665CF7ED747F1197F0C65896ACA11FC7664F642AFC67D5E626FE19AFC35C7746B4D2AB8F6471DDD035024ECB4D92FB970F5CD1AEAB6AB238FE24D4A34668B55CC1E7F17D9123DF8CE4C6DC5BAFB7F1BA452FE797C5124A58560487B26AF4A94D9E3B29A51D3A72E428D917BEAA971EDAC60607F9441CB1D1807E507B0AD7CF296B503A3AB413E1C4202C77593152CD296042949FE27003BABB93E88723D208B833B; playerid=58335676; JSESSIONID-WYYY=gOwOVVnkS%2FFK82XcaNp1zHXs2A2Zdgi%2FdZ%2Ffhav%2BjDEBw7QVF894H42vlsk2hpFrxYv9k6%2FYWpiHmxlw0i%2Bv2rYbT3NUCQPCeiZb%2FBl00UCl1Ztj6g1mFjVmRxn2Isra2%5ClTnSuVmp0pNIr%2FFUh%5C%2FuNY6PJ9cJlrzr2%5Cx13nMrJD6ylD%3A1793105137875; Hm_lpvt_1483fb4774c02a30ffa6f0e2945e9b70=1793103351"

COOKIE = COOKIE.strip() or os.environ.get("MUSIC_COOKIE", "").strip()
if COOKIE:
    H["cookie"] = COOKIE

# 编译 JS 只做一次
ctx = execjs.compile((BASE_DIR / "逆向网易云音乐歌曲.js").read_text(encoding="utf-8"))


def fetch_songs():
    """从榜单页取 [(歌曲id, 歌名), ...]（必须带 UA，否则拿到的是精简页）"""
    html = requests.get(LIST_URL, headers=H, timeout=30).text
    return re.findall(r'<a href="/song\?id=(\d+)">(.*?)</a>', html)


def sign(song_id: str) -> dict:
    """调 JS 给这首歌的参数签名"""
    payload = {
        "ids": f"[{song_id}]",
        "level": "exhigh",
        "encodeType": "mp4",
        "csrf_token": "",
    }
    return ctx.call("get_sign", payload)


def main():
    songs = fetch_songs()
    print(f"榜单共 {len(songs)} 首，本次尝试前 {MAX_SONGS} 首")
    if not COOKIE:
        print("（未设置 MUSIC_COOKIE，只能下免费歌）")

    OUT_DIR.mkdir(exist_ok=True)
    ok = skip = 0

    for i, (sid, name) in enumerate(songs[:MAX_SONGS], 1):
        try:
            js = requests.post(API, headers=H, data=sign(sid), timeout=20).json()
        except Exception as exc:
            print(f"[{i}] {name[:24]} 请求失败：{exc}")
            skip += 1
            continue

        item = (js.get("data") or [{}])[0]
        music_url = item.get("url")

        if not music_url:
            print(f"[{i}] {name[:24]} 跳过（code={item.get('code')}，版权受限）")
            skip += 1
            continue

        content = requests.get(music_url, headers=H, timeout=120).content
        ext = "m4a" if content[4:8] == b"ftyp" else "mp3"
        safe = re.sub(r'[\\/:*?"<>|]', "", name)[:40].strip() or sid
        path = OUT_DIR / f"{sid}_{safe}.{ext}"
        path.write_bytes(content)
        print(f"[{i}] {name[:24]} → {path.name}（{len(content) / 1024 / 1024:.1f} MB）")
        ok += 1

    print(f"\n完成：成功 {ok} 首，跳过 {skip} 首")
    print(f"文件目录：{OUT_DIR}")


if __name__ == "__main__":
    main()
