
import requests
import sys

# User provided proxies
PROXIES_LIST = [
    "socks5://oyyvimta:3olvpyzbkfhq@23.95.150.145:6114",
    "socks5://oyyvimta:3olvpyzbkfhq@198.23.239.134:6540",
    "socks5://oyyvimta:3olvpyzbkfhq@107.172.163.27:6543", 
    "socks5://oyyvimta:3olvpyzbkfhq@198.105.121.200:6462",
    "socks5://oyyvimta:3olvpyzbkfhq@64.137.96.74:6641",
    "socks5://oyyvimta:3olvpyzbkfhq@216.10.27.159:6837",
    "socks5://oyyvimta:3olvpyzbkfhq@23.26.71.145:5628"
]

TARGET = "https://surakarta.go.id"
PATHS = [
    "/.env", 
    "/public/.env", 
    "/.git/HEAD", 
    "/phpmyadmin/", 
    "/admin/", 
    "/up/",
    "/public/up/"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def check_web_vulns():
    print(f"[*] Starting Windows-Compatible Audit for {TARGET}...")
    print(f"[*] Loaded {len(PROXIES_LIST)} proxies.")

    session = requests.Session()
    
    # Try to find a working proxy
    valid_proxy = None
    for p in PROXIES_LIST:
        print(f"[*] Testing proxy: {p.split('@')[1]} ...")
        try:
            session.proxies = {'http': p, 'https': p}
            r = session.get("https://ifconfig.me", timeout=10)
            if r.status_code == 200:
                print(f"[+] Proxy WORKS! IP: {r.text.strip()}")
                valid_proxy = p
                break
        except Exception as e:
            print(f"[-] Proxy Failed: {e}")
            continue
    
    if not valid_proxy:
        print("[-] FATAL: No working proxies found. Cannot proceed safely.")
        return

    print("\n[*] Starting Web Scan...")
    
    # Check ISPConfig Port 8080
    try:
        url_8080 = "https://surakarta.go.id:8080/login/"
        print(f"[*] Checking {url_8080} ...")
        r = session.get(url_8080, headers=HEADERS, verify=False, timeout=15)
        if r.status_code == 200 or "ISPConfig" in r.text or "login" in r.text.lower():
            print(f"[!] VULNERABLE? Found Login Page at {url_8080} (Code: {r.status_code})")
        else:
            print(f"[-] Port 8080 Status: {r.status_code}")
    except Exception as e:
        print(f"[-] Error checking Port 8080: {e}")

    # Check Paths
    for path in PATHS:
        url = TARGET + path
        print(f"[*] Checking {url} ...")
        try:
            r = session.get(url, headers=HEADERS, verify=False, timeout=10)
            if r.status_code == 200:
                print(f"[!] POTENTIAL LEAK: {url} (200 OK) - Size: {len(r.content)}")
            elif r.status_code == 403:
                 print(f"[-] Forbidden (403): {url}")
            else:
                 print(f"[-] Check: {url} (Status: {r.status_code})")
        except Exception as e:
            print(f"[-] Error: {e}")

    print("\n[*] Scan Finished.")

if __name__ == "__main__":
    try:
        check_web_vulns()
    except ImportError:
        print("[-] Error: 'requests' library missing. Install with 'pip install requests pysocks'")
    except Exception as e:
        print(f"[-] Unexpected Error: {e}")
