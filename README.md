# sqlmapauto: Advanced Automated Wrapper for SQLMap

**sqlmapauto** is a powerful Python wrapper designed to automate SQL injection testing with advanced evasion techniques. It simplifies the process of using `sqlmap` by automatically handling proxy rotation, WAF bypass via tamper scripts, and header spoofing.

## 🚀 Features

*   **Smart WAF Bypass**: Automatically loads effective tamper scripts (`space2comment`, `between`, `randomcase`) to evade Web Application Firewalls.
*   **Auto Proxy Rotation**: Randomly selects a high-anonymity SOCKS5/HTTP proxy from a built-in list for each scan.
*   **Header Spoofing**: Injects randomized `User-Agent` and `X-Forwarded-For` headers to masquerade as legitimate traffic.
*   **One-Command-Run**: Pre-configured with optimized settings (`--level=3`, `--risk=2`, `--batch`, `--threads=5`) for maximum efficiency.

## 📋 Requirements

1.  **Python 3.x**
2.  **SQLMap**: You must have `sqlmap` installed. The script assumes `sqlmap` is located at `python sqlmap/sqlmap.py`. You may need to adjust the `SQLMAP_PATH` variable in `sqlmapauto.py` if your installation path differs.

## 🛠️ Installation

```bash
git clone https://github.com/raynaldoanantawijaya/sqlmapauto.git
cd sqlmapauto
```

## 💻 Usage

Run the script by providing the target URL as an argument:

```bash
python sqlmapauto.py <TARGET_URL>
```

### Example

```bash
python sqlmapauto.py "http://example.com/vuln.php?id=1"
```

The script will automatically:
1.  Isolate a working proxy.
2.  Generate a random fake IP for header spoofing.
3.  Execute `sqlmap` with the stealthiest configuration.

## ⚠️ Disclaimer

This tool is for educational purposes and authorized penetration testing only. Do not use this tool on targets you do not have permission to audit. The author is not responsible for any misuse.
