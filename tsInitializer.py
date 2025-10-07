import subprocess
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Tshark continuous capture
def run_tshark_continuous(duration_total=600, output_file="captures/output.csv"):
    """
    Runs tshark continuously for a given total duration in background.
    """
    os.makedirs("captures", exist_ok=True)

    cmd = [
        "tshark",
        "-i", "en0",
        "-a", f"duration:{duration_total}",
        "-f", "tcp port 443 or udp port 443 or tcp port 80",
        "-Y", "tls.handshake.extensions_server_name || http",
        "-T", "fields",
        "-e", "tls.handshake.extensions_server_name",
        "-e", "tls.handshake.extensions_alpn_str",
        "-e", "http.host",              
        "-E", "header=y",
        "-E", "separator=,",
    ]

    print(f"[INFO] Starting continuous tshark capture for {duration_total}s...")
    with open(output_file, "w", encoding="utf-8") as f:
        process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.DEVNULL, text=True)
    return process

def visit_domain(domain, duration=10):
    """
    Opens a single Chrome session (headless), starts with a blank page,
    visits the target domain for the specified duration, then closes.
    """
    print(f"[INFO] Launching Chrome for {domain}")

    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--ignore-certificate-errors")
    chrome_opts.add_argument("--disable-dev-shm-usage")

    # tart Chrome directly on a blank page (no google.com)
    chrome_opts.add_argument("--homepage=about:blank")
    chrome_opts.add_argument("--no-first-run")
    chrome_opts.add_argument("--no-default-browser-check")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_opts)

    try:
        # open about:blank explicitly to avoid startup traffic
        driver.get("about:blank")

        start = time.time()
        driver.get(f"https://{domain}")
        print(f"[INFO] Opened {domain} at {time.strftime('%H:%M:%S', time.localtime(start))}")
        time.sleep(duration)
    except Exception as e:
        print(f"[WARN] Error visiting {domain}: {e}")
    finally:
        driver.quit()
        end = time.time()
        print(f"[INFO] Closed {domain} at {time.strftime('%H:%M:%S', time.localtime(end))}")
        return start, end
