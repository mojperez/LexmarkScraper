import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== CONFIG =====
EXCEL_PATH = r"C:\Users\mojperez\Documents\PRINTERS\CX922de\EXCELPRINTERS.xlsx"
SHEET_NAME = 0
TIMEOUT = 22
MAX_WORKERS = 10

SUPPLIES = {
    "Cyan Cartridge": 1,        # segunda coincidencia
    "Magenta Cartridge": 1,        
    "Yellow Cartridge": 1,        
    "Black Cartridge": 1,        

    "Maintenance Kit Information": 0,  # primera coincidencia (y usualmente única)
    "Waste Toner Bottle": 1,  

    "Cyan Photoconductor":1,
    "Magenta Photoconductor":1,
    "Yellow Photoconductor":1,
    "Black Photoconductor": 1,
    "Black Developer": 1,
    "Color Developer Kit (CMY)": 1,
    "200K HCF Maintenance Kit": 0,
    "200K MPF Maintenance Kit": 0,
    "Fuser": 0


}

COLUMN_MAP = {
    "Cyan Cartridge": "Cyan Cartridge",        
    "Magenta Cartridge": "Magenta Cartridge",        
    "Yellow Cartridge": "Yellow Cartridge",        
    "Black Cartridge": "Black Cartridge",        

    "Maintenance Kit Information": "Maintenance Kit Information",  
    "Waste Toner Bottle": "Waste Toner Bottle", 

    "Cyan Photoconductor": "Cyan Photoconductor",
    "Magenta Photoconductor": "Magenta Photoconductor",
    "Yellow Photoconductor": "Yellow Photoconductor",
    "Black Photoconductor": "Black Photoconductor",
    "Black Developer": "Black Developer",
    "Color Developer Kit (CMY)": "Color Developer Kit (CMY)",
    "200K HCF Maintenance Kit": "200K HCF Maintenance Kit",
    "200K MPF Maintenance Kit": "200K MPF Maintenance Kit",
    "Fuser": "Fuser"





}



# ===== SCRAPING =====
def extract_supply_info_by_index(soup, supply_name, index):
    fonts = [
        f for f in soup.find_all("font")
        if supply_name.lower() in f.get_text(strip=True).lower()
    ]

    if len(fonts) <= index:
        return None

    start_font = fonts[index]
    result = {}

    for table in start_font.find_all_next("table"):
        next_header = table.find("font", attrs={"size": "+2"})
        if next_header and next_header != start_font:
            break

        tds = table.find_all("td")
        if len(tds) == 2:
            key = tds[0].get_text(strip=True)
            value = tds[1].get_text(strip=True)
            if key:
                result[key] = value

    return result


def get_device_supplies(ip):
    url = f"http://{ip}/cgi-bin/menu_settings_page"
    result = {
        "Cyan Cartridge": None,        
        "Magenta Cartridge": None,       
        "Yellow Cartridge": None,        
        "Black Cartridge": None,       

        "Maintenance Kit Information": None,  
        "Waste Toner Bottle": None,  

        "Cyan Photoconductor": None,
        "Magenta Photoconductor": None,
        "Yellow Photoconductor": None,
        "Black Photoconductor": None,
        "Black Developer": None,
        "Color Developer Kit (CMY)": None,
        "200K HCF Maintenance Kit": None,
        "200K MPF Maintenance Kit": None,
        "Fuser": None

    }

    try:
        res = requests.get(url, timeout=TIMEOUT)
        soup = BeautifulSoup(res.content, "html.parser")

        for supply, idx in SUPPLIES.items():
            info = extract_supply_info_by_index(soup, supply, idx)
            if info and "Supply Status" in info:
                result[supply] = info["Supply Status"]

    except Exception as e:
        print(f"❌ Error con {ip}: {e}")

    return ip, result  


# ===== MAIN =====
def main():
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)

    futures = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        for i, row in df.iterrows():
            ip = str(row["DIRECCION (IPV4)"]).strip()

            if not ip or ip.lower() == "nan":
                continue

            futures.append(executor.submit(get_device_supplies, ip))

        for future in as_completed(futures):
            ip, supplies = future.result()

            print(f"✅ Resultado recibido de {ip}")

            # actualizar dataframe
            mask = df["DIRECCION (IPV4)"].astype(str) == ip
            idx = df[mask].index

            if len(idx) > 0:
                i = idx[0]
                for supply, value in supplies.items():
                    df.at[i, COLUMN_MAP[supply]] = value

    df.to_excel("CX922de_mthread.xlsx", index=False)
    df
    print("✅ Excel actualizado y guardado")


if __name__ == "__main__":
    main()

