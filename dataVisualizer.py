import csv
import os
import pandas as pd
import matplotlib.pyplot as plt

def load_rows(capture_file):
    # Read CSV safely (handles '\,') and skip headers/empties.
    rows = []
    with open(capture_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",", escapechar="\\", quoting=csv.QUOTE_NONE)

        for row in reader:
            if not row:
                continue
            # skip obvious header lines
            if "tls.handshake" in row[-1].lower():
                continue
            rows.append(row)
    return rows

def extract_protocols(rows):
    # Return a dict counting only valid negotiated protocols.
    counts = {"h3": 0, "h2": 0, "http/1.1": 0}

    for row in rows:
        # last non-empty cell
        proto_raw = next((c for c in reversed(row) if c.strip()), "").strip().lower()
        if not proto_raw:
            continue

        # pick highest protocol mentioned
        if "h3" in proto_raw:
            counts["h3"] += 1
        elif "h2" in proto_raw:
            counts["h2"] += 1
        elif "http/1.1" in proto_raw:
            counts["http/1.1"] += 1
        # ignore anything else

    # remove zero-count protocols
    counts = {k: v for k, v in counts.items() if v > 0}
    return counts

def plot_distribution(counts):
    # Create and save donut chart (PNG + PDF).
    total = sum(counts.values())
    if total == 0:
        print("[WARN] No recognizable protocols found.")
        return

    pct = (pd.Series(counts) / total * 100).round(2)

    print("\nProtocol Distribution:")
    for proto, val in pct.items():
        print(f"  {proto}: {val:.2f}%")

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        pct,
        labels=[k.upper() for k in pct.index],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops=dict(width=0.35, edgecolor="white"),
    )
    plt.setp(autotexts, size=12, weight="bold", color="black")
    ax.set_title("HTTP Protocol Distribution", fontsize=14, pad=20)
    plt.tight_layout()

    os.makedirs("captures", exist_ok=True)
    png_path = "captures/protocol_distribution.png"
    pdf_path = "captures/protocol_distribution.pdf"
    plt.savefig(png_path, dpi=300)
    plt.savefig(pdf_path)
    print(f"[INFO] Saved chart as:\n  {png_path}\n  {pdf_path}")
    plt.show()

def analyze_protocol_distribution(capture_file="captures/output.csv"):
    print("[INFO] Analyzing protocol distribution...")
    rows = load_rows(capture_file)
    counts = extract_protocols(rows)
    plot_distribution(counts)

if __name__ == "__main__":
    analyze_protocol_distribution()