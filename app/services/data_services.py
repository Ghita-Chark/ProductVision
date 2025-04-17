import pandas as pd
from app.dal.db import insert_data, get_all_products, get_connection


def process_csv(file_path):
    df = pd.read_csv(file_path)

    df = df.rename(columns={'purshase_price': 'purchase_price'})
    df = df.drop_duplicates()
    df = df.dropna()

    numeric_cols = ['section', 'barcode', 'item_num', 'purchase_price', 'selling_price', 'quantity']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    df['from_date'] = pd.to_datetime(df['from_date'], errors='coerce')
    df['from_date'] = df['from_date'].apply(lambda x: x.replace(year=2024) if pd.notnull(x) else x)
    df['from_date'] = df['from_date'].dt.strftime('%Y-%m-%d')
    df = df.dropna(subset=['from_date'])

    expected_columns = ['from_date', 'department', 'section', 'barcode', 'item_num',
                        'item_description', 'purchase_price', 'selling_price', 'quantity']

    missing = [col for col in expected_columns if col not in df.columns]
    if missing:
        print("❌ Colonnes manquantes :", missing)
        return

    records = df[expected_columns].values.tolist()

    if len(records) == 0:
        print("⚠️ Aucun enregistrement valide à insérer.")
        return
    else:
        print(f"✅ {len(records)} enregistrements prêts à l'insertion.")
        print("➡️ Exemple :", records[0])

    insert_data(records)
