#!/usr/bin/env python3
import asyncio
import json
import os
import shutil
import subprocess
import sys
import urllib.request

import nodriver as nd

COOKIE_FILE = "/tmp/nfw_session.json"


def help_msg():
    print("""nfw (nuclei_fuck_waf) — bypass WAF for Nuclei scans

Usage: python3 nfw.py <URL> [nuclei args...]

Examples:
  python3 nfw.py https://target.com
  python3 nfw.py https://target.com -severity high -tags cve
  python3 nfw.py https://target.com -t ~/templates/ -rl 10

First arg = target URL, rest goes straight to Nuclei.""")
    sys.exit(1)


def find_nuclei():
    paths = [
        shutil.which("nuclei"),
        os.path.expanduser("~/go/bin/nuclei"),
        "/usr/local/bin/nuclei",
        "/usr/bin/nuclei",
    ]
    for p in paths:
        if p and os.path.exists(p):
            print(f"[*] Nuclei found: {p}")
            return p
    print("[-] Nuclei not found. Install: go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest")
    sys.exit(1)


def find_chrome():
    paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for p in paths:
        if p and os.path.exists(p):
            print(f"[*] Browser found: {p}")
            return p
    raise FileNotFoundError("Chrome/Chromium not found. Install: sudo apt install chromium")


def geo():
    try:
        with urllib.request.urlopen("https://ipinfo.io/json", timeout=10) as r:
            d = json.loads(r.read().decode())
            return d.get("country", "US"), d.get("ip", "127.0.0.1")
    except Exception as e:
        print(f"[!] Geo failed: {e}")
        return "US", "127.0.0.1"


async def grab_fp(tab):
    cookies = await tab.evaluate("document.cookie")
    
    if not cookies:
        objs = await tab.browser.cookies.get_all()
        cookies = "; ".join([f"{c.name}={c.value}" for c in objs])
    
    ua = await tab.evaluate("navigator.userAgent")
    lang = await tab.evaluate("navigator.languages ? navigator.languages.join(',') : navigator.language")
    plat = await tab.evaluate("navigator.platform")
    
    return cookies, ua, lang, plat


async def main():
    if len(sys.argv) < 2:
        help_msg()

    url = sys.argv[1]
    extra = sys.argv[2:]

    cc, ip = geo()
    chrome = find_chrome()
    nuclei = find_nuclei()
    
    print(f"[*] IP: {ip}")
    print(f"[*] Country: {cc}")
    print(f"[*] Target: {url}")
    if extra:
        print(f"[*] Extra args: {' '.join(extra)}")
    
    br = await nd.start(browser_executable_path=chrome)
    tab = await br.get(url)
    
    print("[*] Chrome opened. Solve challenge, press Enter...")
    input(">>> ")
    
    ck, ua, lang, plat = await grab_fp(tab)
    
    print(f"[+] Plat: {plat}")
    print(f"[+] UA: {ua[:40]}...")
    print(f"[+] Lang: {lang}")
    print(f"[+] Cookies: {'OK (' + str(len(ck)) + ' chars)' if ck else 'EMPTY'}")
    
    br.stop()
    
    if not ck:
        print("[-] Empty cookies. Abort.")
        return
    
    with open(COOKIE_FILE, "w") as f:
        json.dump({
            "target": url,
            "country": cc,
            "ip": ip,
            "agent": ua,
            "locale": lang,
            "platform": plat,
            "cookies": ck
        }, f, indent=2)
    
    cmd = [
        nuclei,
        "-u", url,
        "-H", f"User-Agent: {ua}",
        "-H", f"Accept-Language: {lang}",
        "-H", f"Cookie: {ck}",
        "-rl", "2",
        "-c", "1",
        "-ni",
        "-timeout", "15",
        "-stats",
        "-v",
        "-o", f"nuclei-report-{cc.lower()}.txt"
    ]

    cmd.extend(extra)
    
    print(f"\n[*] Scanning...")
    print(f"[*] Cmd: nuclei -u {url} ...")
    subprocess.run(cmd)


if __name__ == "__main__":
    asyncio.run(main())