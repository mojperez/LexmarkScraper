import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== CONFIG =====
EXCEL_PATH = r"C:\Users\mojperez\Documents\PRINTERS\532\EXCELPRINTERS.xlsx"
SHEET_NAME = 0
TIMEOUT = 22
MAX_WORKERS = 10

SUPPLIES = {
    "Cyan Cartridge": 1,        # segunda coincidencia
    "Magenta Cartridge": 1,        # segunda coincidencia
    "Yellow Cartridge": 1,        # segunda coincidencia
    "Black Cartridge": 1,        # segunda coincidencia

    "Imaging Kit": 1,     # segunda coincidencia
    "Maintenance Kit Information": 0,  # primera (y usualmente única)
    "Waste Toner Bottle": 1  # primera (y usualmente única)
}

COLUMN_MAP = {
    "Cyan Cartridge": "Cyan Cartridge",        # segunda coincidencia
    "Magenta Cartridge": "Magenta Cartridge",        # segunda coincidencia
    "Yellow Cartridge": "Yellow Cartridge",        # segunda coincidencia
    "Black Cartridge": "Black Cartridge",        # segunda coincidencia

    "Imaging Kit": "Imaging Kit",     # segunda coincidencia
    "Maintenance Kit Information": "Maintenance Kit Information",  # primera (y usualmente única)
    "Waste Toner Bottle": "Waste Toner Bottle"  # primera (y usualmente única)
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
        "Cyan Cartridge": None,        # segunda coincidencia
        "Magenta Cartridge": None,        # segunda coincidencia
        "Yellow Cartridge": None,        # segunda coincidencia
        "Black Cartridge": None,        # segunda coincidencia

        "Imaging Kit": None,     # segunda coincidencia
        "Maintenance Kit Information": None,  # primera (y usualmente única)
        "Waste Toner Bottle": None  # primera (y usualmente única)
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

    return ip, result  # 🔥 devolvemos también el IP


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

    df.to_excel("CX532adwe_mthread.xlsx", index=False)
    df
    print("✅ Excel actualizado y guardado")


if __name__ == "__main__":
    main()

