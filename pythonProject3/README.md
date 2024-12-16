***************************************************************************************************************
***************************************************************************************************************
**                                     name: electrion_scraper.py                                            **                                                        
**                                     author: Martina Volrábová                                             **
**                                     python ver: 3.6                                                       **
**                                     srcipt ver: 1.00                                                      **
***************************************************************************************************************
** Changelog: 2024/12/05 - first written                                                                     **
***************************************************************************************************************
***************************************************************************************************************
Skript psaný v Python verzi 3.6 stahuje volební výsledky do českého parlamentu z roku 2021 za jednotlivé územní celky.
Na základě URL územního celku stáhne volební data obcí (včetně těch s více okrsky), agreguje výsledky okrsků a uloží výsledky do CSV.

INSTALL:
1. Ve Windows stiskni Win + R, napiš cmd a stiskni Enter.
2. Přejdi do složky projektu např cd C:\Users\Admin\Desktop\Ukol_3\pythonProject3
3. Vytvoř nové virtuální prostředí pomocí příkazu python -m venv .venv
4. Aktivujte vytvořené prostředí příkazem: .venv\Scripts\activate
5. Nainstaluj potřebné knihovny z requirements.txt, který se nachází v adresáři pythonProject3: "pip install -r requirements.txt"
6. Spusť script příkazem: python electrion_scraper.py "https://www.volby.cz/pls/ps2021/ps32?xjazyk=CZ&xkraj=14&xnumnuts=8103" "vysledky_karvina.csv"

ARGUEMNTS:
Script vyžaduje vyplnit 2 vstupní argumenty
* base_url - odkaz na územní celek například odkaz na územní celek Karviná: "https://www.volby.cz/pls/ps2021/ps32?xjazyk=CZ&xkraj=14&xnumnuts=8103"
* output_file - název cílového csv souboru např. "vysledky_karvina.csv"
* Spusť script příkazem: python electrion_scraper.py "https://www.volby.cz/pls/ps2021/ps32?xjazyk=CZ&xkraj=14&xnumnuts=8103" "vysledky_karvina.csv"

USED LIBRARIES:
* beautifulsoup4==4.12.3
* certifi==2024.8.30
* charset-normalizer==2.0.12
* idna==3.10
* requests==2.27.1
* soupsieve==2.3.2.post1
* urllib3==1.26.20

OUTPUT EXAMPLE:
Výstup z běhu python electrion_scraper.py "https://www.volby.cz/pls/ps2021/ps32?xjazyk=CZ&xkraj=14&xnumnuts=8103" "vysledky_karvina.csv"
je uložen v adresáři ../pythonProject3/Karvina.csv




