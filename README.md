# nfw - nuclei_fuck_waf

**Bypass WAF for Nuclei scans using browser fingerprinting**

## What is this?

`nfw` is a wrapper for Nuclei that helps bypass WAF (Web Application Firewall) by capturing real browser fingerprints after solving JavaScript challenges (Cloudflare, DDoS-Guard, etc.).

![Demo](video.gif)

## Features

- Automatically launches Chrome/Chromium to solve captchas and JS challenges
- Captures cookies, User-Agent, language, and platform
- Passes all collected data to Nuclei
- Automatically detects your country and IP

## Principle

1. **Open** target in real Chrome
2. **Solve** CAPTCHA/challenge manually
3. **Steal** cookies, User-Agent, platform info
4. **Feed** stolen fingerprint to Nuclei
5. **Scan** like a legit user

WAF sees real browser → lets you through.

## Installation

1. **Download:**
     ```
     git clone https://github.com/Sergei768/nuclei_fuck_waf/
     ```

2. **Create and activate virtual environment:**
     ```
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```
   pip install nodriver
   ```

4. **Make executable:**
   ```
   chmod +x nfw.py
   ```

## Usage

**Syntax**
```
python3 nfw.py <URL> [nuclei args...]
```

**Examples**

**Basic scan:**
```
python3 nfw.py https://example.com
```

**Scan only high/critical vulnerabilities:**
```
python3 nfw.py https://example.com -severity high,critical
```

**Use custom templates:**
```
python3 nfw.py https://example.com -t ~/nuclei-templates/cves/
```

**Change request rate:**
```
python3 nfw.py https://example.com -rl 10 -c 5
```

## How it works

1. Detects your IP and country via ipinfo.io
2. Opens browser with the target URL
3. You manually solve the WAF challenge (captcha, Cloudflare, etc.)
4. Script captures cookies and other browser parameters
5. Runs Nuclei with the captured headers and cookies

## Default Nuclei parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `-rl` | 2 | Requests per second limit |
| `-c` | 1 | Concurrent threads |
| `-ni` | true | No interactions |
| `-timeout` | 15 | Request timeout (seconds) |
| `-stats` | true | Show statistics |
| `-v` | true | Verbose output |


