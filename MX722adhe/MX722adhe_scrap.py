import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== CONFIG =====
EXCEL_PATH = r"C:\Users\mojperez\Documents\PRINTERS\722adhe\722adhePRINTERS.xlsx"
SHEET_NAME = 0
TIMEOUT = 22
MAX_WORKERS = 10  # 

SUPPLIES = {
    "Black Cartridge": 1,
    "Black Imaging Unit": 1,
    "Maintenance Kit Information": 0
}

COLUMN_MAP = {
    "Black Cartridge": "CARTUCHO NEGRO",
    "Black Imaging Unit": "Unidad de imagen",
    "Maintenance Kit Information": "Kit de mantenimiento"
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
        "Black Cartridge": None,
        "Black Imaging Unit": None,
        "Maintenance Kit Information": None
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

    df.to_excel("MX722adhe_scrap.xlsx", index=False)
    print("✅ Excel actualizado y guardado")


if __name__ == "__main__":
    main()
