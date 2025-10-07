import csv

# Read domains from CSV
def get_domains_from_csv(filepath="data/mostVisited50.csv"):
    # Reads semicolon-separated CSV file, returns list of domains (first column).
    domains = []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if row:
                domains.append(row[0].strip())
    if domains and not ("." in domains[0]):  # skip header if needed
        domains = domains[1:]
    return domains