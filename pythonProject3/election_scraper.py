import sys
import requests
from bs4 import BeautifulSoup
import csv
import argparse

def validate_arguments(base_url, output_file):
    """Validuje vstupní argumenty."""

    # Zkontroluj, zda byly zadány oba argumenty
    if not base_url or not output_file:
        print("Chyba: Musíte zadat oba argumenty - URL zdroje dat a cestu k výstupnímu souboru.")
        sys.exit(1)

    # Zkontroluj, zda URL vypadá jako platný odkaz
    if not base_url.startswith("https://"):
        print("Chyba: První argument musí být URL začínající 'https://'.")
        sys.exit(1)

    # Zkontroluj, zda výstupní soubor má příponu .csv
    if not output_file.endswith(".csv"):
        print("Chyba: Druhý argument musí být cesta k souboru s příponou '.csv'.")
        sys.exit(1)

def get_obec_links(base_url):
    """Stáhni všechny odkazy na detailní stránky obcí."""
    try:
        response = requests.get(base_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Chyba při stahování: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all("a", href=True):
        if "xobec=" in link["href"]:
            links.append("https://www.volby.cz/pls/ps2021/" + link["href"])
    return links

def get_okrsek_links(obec_url):
    """Stáhni všechny odkazy na okrsky v obci."""
    try:
        response = requests.get(obec_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Chyba při stahování: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all("a", href=True):
        if "xokrsek=" in link["href"]:
            links.append("https://www.volby.cz/pls/ps2021/" + link["href"])
    return links

def parse_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Získej název obce z URL
    h3_elements = soup.find_all("h3")
    nazev_obce = None
    for h3 in h3_elements:
        if "Obec:" in h3.text:
            nazev_obce = h3.text.replace("Obec:", "").strip()
            break

    if not nazev_obce:
        print("Error: Název obce nenalezen.")
        sys.exit(1)

    #Stáhni volební data z první tabulky (voliči, vydané obálky, platné hlasy)
    volici_elem = soup.find("td", {"headers": "sa2"})
    vydane_obalky_elem = soup.find("td", {"headers": "sa3", "data-rel": "L1"})
    platne_hlasy_elem = soup.find("td", {"headers": "sa6"})

    def clean_number(text):
        """Zkontroluj zda je údaj číselná hodnota, pokud není, převeď na 0"""
        # Odstranní Unicode non-breaking space z číselnýh hodnot > 1000
        text = text.replace("\xa0", "").replace(" ", "").strip()
        # Pokud je hodnota číslo, return int, jinak 0
        return int(text) if text.isdigit() else 0

    volici = clean_number(volici_elem.text)
    vydane_obalky = clean_number(vydane_obalky_elem.text)
    platne_hlasy = clean_number(platne_hlasy_elem.text)

    hlasy_stran = {}
    tabs = soup.find_all("table", {"class": "table"})
    for single_tab in tabs:
        rows = single_tab.find_all("tr")
        for row in rows:
            nazev_elem = row.find("td", {"headers": lambda x: x and x.endswith("t1sb2") or x.endswith("t2sb2")})
            hlasy_elem = row.find("td", {"headers": lambda x: x and x.endswith("t1sb3") or x.endswith("t2sb3")})

            if nazev_elem and hlasy_elem:
                nazev_strany = nazev_elem.text.strip()
                hlasy = clean_number(hlasy_elem.text)
                hlasy_stran[nazev_strany] = hlasy

    obec_data = {
        "název_obce": nazev_obce,
        "voliči": volici,
        "vydané obálky": vydane_obalky,
        "platné hlasy": platne_hlasy,
        "hlasy_stran": hlasy_stran,
    }
    return obec_data

def aggregate_data(data_list):
    """Agreguje data z více okrsků do jednoho celku."""
    aggregated = {
        "název_obce": data_list[0]["název_obce"],
        "voliči": 0,
        "vydané obálky": 0,
        "platné hlasy": 0,
        "hlasy_stran": {},
    }
    for data in data_list:
        aggregated["voliči"] += data["voliči"]
        aggregated["vydané obálky"] += data["vydané obálky"]
        aggregated["platné hlasy"] += data["platné hlasy"]
        for strana, hlasy in data["hlasy_stran"].items():
            aggregated["hlasy_stran"][strana] = aggregated["hlasy_stran"].get(strana, 0) + hlasy
    return aggregated

def save_to_csv(obce_data, output_file):
    """Ulož data do CSV."""
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        all_parties = set()
        for obec in obce_data.values():
            all_parties.update(obec["hlasy_stran"].keys())
        all_parties = sorted(all_parties)

        header = ["Kód obce", "Název obce", "Voliči", "Vydané obálky", "Platné hlasy"] + all_parties
        writer.writerow(header)

        for kod_obce, obec in obce_data.items():
            row = [
                kod_obce,
                obec["název_obce"],
                obec["voliči"],
                obec["vydané obálky"],
                obec["platné hlasy"],
            ] + [obec["hlasy_stran"].get(strana, "0") for strana in all_parties]
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="Stáhni výsledky voleb do českého parlamentu 2021 a ulož data do CSV.")
    parser.add_argument("base_url", help="URL hlasování za jeden územní celek.")
    parser.add_argument("output_file", help="Cesta k cílovému CSV souboru včetně názvu.")
    args = parser.parse_args()

    # Validace vstupních argumentů
    validate_arguments(args.base_url, args.output_file)

    # Získání hodnot argumentů
    base_url = args.base_url
    output_file = args.output_file

    # Získání odkazů na obce
    obec_links = get_obec_links(base_url)
    print(f"Nalezeno {len(obec_links)} obcí k zpracování.")

    obce_data = {}
    for link in obec_links:
        print(f"Zpracovávám: {link}")
        okrsek_links = get_okrsek_links(link)
        if okrsek_links:
            print(f"Obec s více okrsky: {link}")
            okrsek_data = [parse_data(requests.get(okrsek_link).text) for okrsek_link in okrsek_links]
            aggregated_data = aggregate_data(okrsek_data)
            kod_obce = link.split("xobec=")[1].split("&")[0]
            obce_data[kod_obce] = aggregated_data
        else:
            print(f"Obec bez okrsků: {link}")
            obec_data = parse_data(requests.get(link).text)
            kod_obce = link.split("xobec=")[1].split("&")[0]
            obce_data[kod_obce] = obec_data

    save_to_csv(obce_data, output_file)
    print(f"Data byla uložena do souboru: {output_file}")

if __name__ == "__main__":
    main()
