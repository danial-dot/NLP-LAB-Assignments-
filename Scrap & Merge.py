import importlib
import csv
import os
import re
import subprocess
import sys


def ensure_package(module_name, package_name=None):
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        package = package_name or module_name
        print(f"[INFO] Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return importlib.import_module(module_name)


requests = ensure_package("requests")
BeautifulSoup = ensure_package("bs4").BeautifulSoup

def scrape_all_countries():

    os.makedirs("countries_data", exist_ok=True)

    url = "https://en.wikipedia.org/wiki/List_of_sovereign_states"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    countries = []

    # Extract country names from table
    tables = soup.find_all("table", {"class": "wikitable"})
    for table in tables:
        for row in table.find_all("tr")[1:]:
            link = row.find("a")
            if link and link.get("href"):
                name = link.text.strip()
                countries.append(name)

    countries = list(set(countries))

    print(f"[INFO] Found {len(countries)} countries")

    data = []

    for country in countries:
        try:
            page_url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
            res = requests.get(page_url, headers=headers)

            if res.status_code != 200:
                continue

            page = BeautifulSoup(res.text, "html.parser")

            paragraphs = page.find_all("p")

            text = ""
            for p in paragraphs:
                content = p.get_text().strip()
                if content:
                    text += content + "\n"

            
            text = re.sub(r"\[\d+\]", "", text)

            if len(text) < 500:
                continue

            safe_name = re.sub(r'[^a-zA-Z0-9_]', '', country.lower().replace(' ', '_'))
            filename = f"countries_data/{safe_name}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)

            data.append([country, text])

            print(f"[✔] Saved: {country}")

        except Exception as e:
            print(f"[✘] Error: {country}")

    # Step 3: Create CSV dataset
    with open("global_countries_dataset.csv", "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Country", "Text"])
        writer.writerows(data)

    print("\n DONE!")
    print(" Individual files saved in 'countries_data/'")
    print(" Master dataset: global_countries_dataset.csv")


if __name__ == "__main__":
    scrape_all_countries()
