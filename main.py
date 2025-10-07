import time
import os
from csvReader import get_domains_from_csv
from tsInitializer import run_tshark_continuous, visit_domain
from dataVisualizer import analyze_protocol_distribution


def main():
    domains = get_domains_from_csv("data/mostVisited50.csv")
    visit_duration = 60     # seconds per domain
    tshark_warmup = 2       # seconds for tshark to start
    total_duration = visit_duration * len(domains) + tshark_warmup + 5

    # Start tshark in background
    tshark_proc = run_tshark_continuous(duration_total=total_duration)
    print("[INFO] Waiting for tshark to initialize...")
    time.sleep(tshark_warmup)

    # Sequentially visit domains
    os.makedirs("captures", exist_ok=True)
    for domain in domains:
        visit_domain(domain, duration=visit_duration)
        time.sleep(2)

    # Wait for tshark to finish
    tshark_proc.wait()
    print("\n✅ All captures finished.")
    print("[INFO] Tshark output saved to captures/output.csv")


if __name__ == "__main__":
    main()